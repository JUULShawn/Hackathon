# -*- coding: utf-8 -*-
"""
This module is used for taking an input of xml and outputing a translated object of translations
"""
from pprint import pprint
from google.cloud import translate
import xml.etree.ElementTree as ET
import six
#Initializing Global translate object
TRANSLATE_CLIENT = translate.Client()
INCLUDED_TAGS = {"description", "meta", "short_description", "text"}


def translate_text(obj, target_languages):
    """
    translates text from english to a few different functions
    """
    language_output = {}
    text_obj = obj.getroot()
    encoded_translation = ""
    temp_text_obj = text_obj
    for lang in target_languages:
        for elem in text_obj.iter():
            if(elem.tag == "text"):
                pass
            elif(elem.tag in INCLUDED_TAGS):
                try:
                    translation = TRANSLATE_CLIENT.translate(
                        str(elem.text),
                        target_language=target_languages[lang],
                        model=translate.BASE
                    )
                except Exception as e:
                    print(elem.text)
                    print(e)
                    continue
                encoded_translation = translation['translatedText'].encode("UTF-8")
                elem.text = encoded_translation
        obj.write(lang + ".xml")
        language_output[lang] = text_obj
        text_obj = temp_text_obj

# def translate_line(line, language):
#     try:
#         translation = TRANSLATE_CLIENT.translate(
#             line,
#             target_language=language,
#             model=translate.BASE
#         )
#     except Exception as e:
#         print(line)
#         # print(e)
#         continue

def parse_html(text):
    """
    parses html and edits the xml files
    """

def read_cloud_storage_buckets():
    """
    read cloud storage buckets 
    """

def parse_xml(text_obj):
    """
    test for parsing xml objects
    """
    for elem in text_obj.iter():
        if(elem.tag in INCLUDED_TAGS):
            print(elem.text)

def get_langauges():
    """
    test function to get languages supported to make sure object is correct
    """
    print TRANSLATE_CLIENT.get_languages()

if __name__ == "__main__":
    #target langauges :French, Korean, German,
    #Polish, Russian, Spanish, Italian and Hebrew.
    LANGUAGES = {
        "French" : "fr",
        "Korean" : "ko",
        "German" : "de",
        "Polish" : "pl",
        "Russian": "ru",
        "Spanish": "es",
        "Italian": "it",
        "Hebrew" : "he"
    }
    xml_obj = ET.parse("test.xml")
    # xml_str = ET.tostring(xml_obj, encoding='utf8', method='xml')
    # parse_xml(xml_obj)
    pprint(translate_text(xml_obj, LANGUAGES))
    # get_langauges()
