## Introduction
The project consists of creating a web application. The main aim of the application is to store plenty of cookbook
recipes within several languages.

The web application (app) will support the uploading of recipes from people
whose use this website. These recipes won’t be uploaded in a usual method,
but they are performed through just buttons (MagicButtons) which render stuff and elements utilized in kitchen. 
Combination these MagicButtons build sentences whose aim is to detail a cooking recipes. 

The sentences are produced via a algorithm which uses treatment language methods, these will explain behind.
I’d like to emphasize that users could upload a new recipe into the application
without pushing any keys. Moreover, involves that a new cooking recipe could
be added into the website in less than five minutes.

Next main point in the app consists on the idea that cooking recipes have
full support for internationalization, whether a German user wants to upload a
new recipe, he’ll manipulate app totally in his language, and he’ll realize every
steps to upload a new recipe this language. When he saves the cooking recipe
and uploads it, other users may read it within any language that is available in
the application.

To finish up and as last point, the application includes a tool to search cooking recipes, 
it is a browser where people can pick ingredient list and similarity level and then app returns the 
recipes whose ingredients are chosen and with passed similarity level.

This project was implemented as university project, [see documentation here](https://drive.google.com/file/d/0B0m3f9uIC1OyOEhTMTl1Y1BPbjg/view?usp=sharing)


## Developed techniques

### Natural Language Generation (NLG) 

Natural Language Generation (NLG) is the natural language processing task of generating natural language from a machine representation system such as a knowledge base or a logical form. Psycholinguists prefer the term language production when such formal representations are interpreted as models for mental representations.

In a sense, one can say that an NLG system is like a translator that converts a computer based representation into a natural language representation. However, the methods to produce the final language are very different from those of a compiler due to the inherent expressivity of natural languages. The simplest examples are systems that generate form letters. Such sys-
tems do not typically involve grammar rules, but may generate a letter to a consumer, e.g. stating that a credit card spending limit is about to be reached.

More complex NLG systems dynamically create texts to meet a communicative
goal. As in other areas of natural language processing, this can be done using
either explicit models of language (e.g., grammars) and the domain, or using
statistical models derived by analysing human-written texts.
In the case that somebody is interesed to program this kind of software, python has a huge kit of tools to handle natural language, it is called NATURAL LANGUAGE TOOLKIT (nltk). Open source Python modules, linguistic data and documentation for research and development in natural language pro-
cessing and text analytics, with distributions for Windows, Mac OSX and Linux.

You can find its large documentation in the following website :
http://www.nltk.org/documentation

### Syntactic Analysis (Parsing) 

In computer science and linguistics, parsing,
or, more formally, syntactic analysis, is the process of analyzing a text, made of a sequence of tokens (for example, words), to determine its grammatical structure with respect to a given (more or less) formal grammar. 
Parsing can also be used as a linguistic term, especially in reference to how phrases are divided
up in garden path sentences.

Parsing is a common term used in psycholinguistics when describing language
comprehension. In this context, parsing refers to the way that human beings,
rather than computers, analyze a sentence or phrase (in spoken language or
text) "in terms of grammatical constituents, identifying the parts of speech,
syntactic relations, etc." This term is especially common when discussing what
linguistic cues help speakers to parse garden-path sentences.
In computing, a parser is one of the components in an interpreter or compiler,
which checks for correct syntax and builds a data structure (often some kind of
parse tree, abstract syntax tree or other hierarchical structure) implicit in the
input tokens. The parser often uses a separate lexical analyser to create tokens
from the sequence of input characters. Parsers may be programmed by hand or
may be (semi-)automatically generated (in some programming languages) by a
tool.

To program using this method there are several python modules 4 PyPars-
ing is one of the most powerful module and most up to date. You can check its documentation in the following website :
http://pyparsing.wikispaces.com/

## How to use it
The application needs to work on a web server. This server must be execute as Django Server and then we have to install Django and many differents libraries. The application is programmed in Django v1.3 and Python v2.7 then it is recommended creating a virtual environment to install every things and then our operative system remains stable. The installation guide has the following
points:

### Step1
Starting the instalation we have to install in our operative system the
package virtualenv v1.6.4 8
.
### Step 2
The packages mysql-client and mysql-server must be installed. When
these packages are installed you have to create a database with the name
db_wikichef. The commands will be:
```bash
$> mysql -u root -p
(mysql) pass : ******
(mysql) CREATE DATABASE db_wikichef
```

### Step 3
When this package is installed we need to create a virtual enviroment in
a folder with the command:
```bash
$> virtualenv –no-site-package –distribute -p python2.7 ’path_to_virtual_env’
```

### Step 4
If the virtual environment was created corretly, in the current folder exe-
cute the following command to start the virtual environment.

```bash
$ . virtual/bin/activate
```

### Step 5
When you want to start the virtual enviroment, you have to execute the last command. Now, it is necesary installing the modules used in the application :

```bash
(virtual)$ pip install django
(virtual)$ pip install pil
(virtual)$ pip install mysql-python
(virtual)$ pip install simplejson
```

### Step 6
Working on the virtual enviroment in the project folder (...wikichef/), we
edit the file settings.py. Into the file in DATABASE section we write the
name and pass of our mysql account.

### Step 7
Every configuration is already. Now we have to start the django server
using the following command inside of the wikichef folder :

```bash
(virtual)$ python manage.py runserver
```

### Step 8
Last step is in Google Chrome we have to write the URL :

http://127.0.0.1:8000/recipes/main
