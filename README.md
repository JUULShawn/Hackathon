Google Cloud Hackathon
===========================
> JUUL Labs + Google Cloud Hackathon (10/1/19)

```
Contributors: Trevor Davenport, Michael Cervantez, Ryan Boyle, Shawn O'Donnell, Joey Wasko, Shreyas Ramanujam, Vincent Lo
```

### Overview ###
```
ServiceNow Automated Document Translation & Data Loss Prevention leveraging Google Cloud Environment + GCP APIs.

APIs: Google Cloud Translate (https://cloud.google.com/translate/docs/translating-text)
      Cloud Data Loss Prevention (https://cloud.google.com/dlp/)
      Google Cloud Storage (https://cloud.google.com/storage/)
      Google Cloud Functions (https://cloud.google.com/functions/)
      ServiceNow API (https://developer.servicenow.com/app.do#!/rest_api_doc?v=madrid&id=c_TableAPI)
```

### Environmental Diagram ###
![](https://i.imgur.com/DdLZbnV.jpg)


### Workflow ###
```
1 [*] Query ServiceNow API's for Documents to Translate
2  [*] Push Document to Google Cloud Storage Bucket
3   [*] Run Google DLP Analysis on Bucket
4    [*] Run Translate API on amended Document
5     [*] Collect Metrics on translation / Document
6      [*] Push Translated & Analyzed file back to sNOW
```
