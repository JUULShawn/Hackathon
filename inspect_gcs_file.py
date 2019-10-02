def inspect_gcs_file(project, bucket, filename, topic_id, subscription_id,
                     info_types, custom_dictionaries=None,
                     custom_regexes=None, min_likelihood=None,
                     max_findings=None, timeout=300):
    """Uses the Data Loss Prevention API to analyze a file on GCS.
    Args:
        project: The Google Cloud project id to use as a parent resource.
        bucket: The name of the GCS bucket containing the file, as a string.
        filename: The name of the file in the bucket, including the path, as a
            string; e.g. 'images/myfile.png'.
        topic_id: The id of the Cloud Pub/Sub topic to which the API will
            broadcast job completion. The topic must already exist.
        subscription_id: The id of the Cloud Pub/Sub subscription to listen on
            while waiting for job completion. The subscription must already
            exist and be subscribed to the topic.
        info_types: A list of strings representing info types to look for.
            A full list of info type categories can be fetched from the API.
        min_likelihood: A string representing the minimum likelihood threshold
            that constitutes a match. One of: 'LIKELIHOOD_UNSPECIFIED',
            'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY'.
        max_findings: The maximum number of findings to report; 0 = no maximum.
        timeout: The number of seconds to wait for a response from the API.
    Returns:
        None; the response from the API is printed to the terminal.
    """

    # Import the client library.
    import google.cloud.dlp

    # This sample additionally uses Cloud Pub/Sub to receive results from
    # potentially long-running operations.
    import google.cloud.pubsub

    # This sample also uses threading.Event() to wait for the job to finish.
    import threading

    # Instantiate a client.
    dlp = google.cloud.dlp.DlpServiceClient()

    # Prepare info_types by converting the list of strings into a list of
    # dictionaries (protos are also accepted).
    if not info_types:
        info_types = ['FIRST_NAME', 'LAST_NAME', 'EMAIL_ADDRESS', 'CREDIT_CARD_NUMBER', 'GCP_CREDENTIALS', 'IP_ADDRESS', 'PHONE_NUMBER', 'DOMAIN_NAME', 'PASSWORD', 'LOCATION']
    info_types = [{'name': info_type} for info_type in info_types]

    # Prepare custom_info_types by parsing the dictionary word lists and
    # regex patterns.
    if custom_dictionaries is None:
        custom_dictionaries = []
    dictionaries = [{
        'info_type': {'name': 'CUSTOM_DICTIONARY_{}'.format(i)},
        'dictionary': {
            'word_list': {'words': custom_dict.split(',')}
        }
    } for i, custom_dict in enumerate(custom_dictionaries)]
    if custom_regexes is None:
        custom_regexes = []
    regexes = [{
        'info_type': {'name': 'CUSTOM_REGEX_{}'.format(i)},
        'regex': {'pattern': custom_regex}
    } for i, custom_regex in enumerate(custom_regexes)]
    custom_info_types = dictionaries + regexes

    # Construct the configuration dictionary. Keys which are None may
    # optionally be omitted entirely.
    inspect_config = {
        'info_types': info_types,
        'custom_info_types': custom_info_types,
        'min_likelihood': min_likelihood,
        'limits': {'max_findings_per_request': max_findings},
    }

    # Construct a storage_config containing the file's URL.
    url = 'gs://{}/{}'.format(bucket, filename)
    storage_config = {
        'cloud_storage_options': {
            'file_set': {'url': url}
        }
    }

    # Convert the project id into a full resource id.
    parent = dlp.project_path(project)

    # Tell the API where to send a notification when the job is complete.
    actions = [{
        'jobNotificationEmails': {}
    }]

    # Construct the inspect_job, which defines the entire inspect content task.
    inspect_job = {
        'inspect_config': inspect_config,
        'storage_config': storage_config,
        'actions': actions,
    }

    operation = dlp.create_dlp_job(parent, inspect_job=inspect_job)

    # Create a Pub/Sub client and find the subscription. The subscription is
    # expected to already be listening to the topic.
    subscriber = google.cloud.pubsub.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project, subscription_id)

    # Set up a callback to acknowledge a message. This closes around an event
    # so that it can signal that it is done and the main thread can continue.
    job_done = threading.Event()

    def callback(message):
        try:
            if (message.attributes['DlpJobName'] == operation.name):
                # This is the message we're looking for, so acknowledge it.
                message.ack()

                # Now that the job is done, fetch the results and print them.
                job = dlp.get_dlp_job(operation.name)
                if job.inspect_details.result.info_type_stats:
                    for finding in job.inspect_details.result.info_type_stats:
                        print('Info type: {}; Count: {}'.format(
                            finding.info_type.name, finding.count))
                else:
                    print('No findings.')

                # Signal to the main thread that we can exit.
                job_done.set()
            else:
                # This is not the message we're looking for.
                message.drop()
        except Exception as e:
            # Because this is executing in a thread, an exception won't be
            # noted unless we print it manually.
            print(e)
            raise

    subscriber.subscribe(subscription_path, callback=callback)
    finished = job_done.wait(timeout=timeout)
    if not finished:
        print('No event received before the timeout. Please verify that the '
              'subscription provided is subscribed to the topic provided.')