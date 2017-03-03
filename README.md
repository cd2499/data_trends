GM Customer Sentiment Analysis 
Version 1.0 
12/07/2016


GENERAL NOTES
-------------------------------------------
- This application is the product of the GM Customer Sentiment Analysis group,
Fall 2016 (WI)Sr Proj&Cputr Ethics Sec 002 (CSC_4996_1609_002)
- Team Member Roster:
    Catherine Celice (Team Lead)
    Greg Olkowski
    James Ross
    Sanjana Shahreen
    Brendan Thull
- The application runs on Python 2.x. 
- The application works with HBase 1.2.x and Hadoop 2.x. Future developers to the project should take care in choosing their HBase/Hadoop version combinations (not all versions of HBase are supported by all versions of Hadoop). It is suggested to review the following website to be sure the chosen combination works well together: https://hbase.apache.org/book.html
- The webui relies on the Django framework (built with python)
   

ABOUT THE APPLICATION
-------------------------------------------
- The application provides two options, the end user can:
    1) Run a sentiment analysis of chosen cars. This option uses customer reviews from the data source for the analysis.
    2) Run a ranking of chosen cars with scores that were provided directly from the data source.
- The source for the data was captured from Edmunds.com. The data consists of user reviews 
  of cars which includes scoring of aspects and comments.
- The sentiment analysis process relies on the NLTK library for natural language processing. 
- This application uses a binomial Naive Bayes classifier that was trained on unigrams from manually trained data sets. 
- The sentiment analysis algorithm also applies polarity compiled from a collection of words scored as positive/negative from sentiwordnet.
- To re-train the classifier, run the "setup_sent_analysis.py" script.


LICENSING INFORMATION
-------------------------------------------
Apache Hadoop 2.x: http://www.apache.org/licenses/
Apache HBase: https://hbase.apache.org/license.html
Django: https://github.com/django/django/blob/master/LICENSE.python
Edmunds.com: http://developer.edmunds.com/terms_of_service/index.html
Python 2.x: https://docs.python.org/2/license.html


CONTACT INFO 
-------------------------------------------
For additional information, feel free to contact the following developers
Greg Olkowski (golkowski01@gmail.com)
James Ross (RossJam78@gmail.com)
Brendan Thull (BrendanWThull@gmail.com)
Catherine Celice (Catherine@wayne.edu)
Sanjana Shahreen(shahreen_168@hotmail.com)
  
