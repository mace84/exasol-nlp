# Exasol Showcase
A showcase illustrating how to use natural language processing methods in an 
Exasol ELT pipeline.

## Use Case: Aspect Based Sentiment Analysis
A gaming company is interested in which aspects of their games are mentioned in game reviews and how these aspects are perceived by the reviewers. The sentiment analysis of game aspects provides insights into viable strategies for game improvement.

This repo implements a simple aspect based sentiment analysis as an exasol user defined function (UDF) and utilizes it in an ELT process, that is administered by areto's [Data Chef](https://github.com/areto-consulting-gmbh/Data-Chef/).

The analysis is performed on a data set of 6.5 mio. game review from [STEAM](https://store.steampowered.com/reviews/). Details on the aspect based sentiment analysis algorith can be found in `./casestudy/`.

In order to execute the NLP pipeline as a UDF, this repo implements a python3 flavor for EXASOL scripting languages in the submodule `./script-languages/`. The flavor is refered to as `python3-nlp-EXASOL-6.<version>`. The NLP flavor is based on Exasol's data science flavor but adds important NLP modules such as [spacy](https://spacy.io/) and [NLTK](https://www.nltk.org/) with the language models used for the aspect based similarity scroring algorithm.

## Exasol config

### Koffer
Connection string:  
10.1.5.29:8563

#### DataChef
http://10.1.5.29:4567   

#### EXASolution
https://10.1.5.29:8443

`/buckets/bucketfs1/languages`  
read PW: `readme2`  
write PW: `writeme2`

curl -i -X PUT -T test.txt http://w:writeme@10.1.5.29:8581/languages/test.txt
curl -i -X PUT -T test.txt http://w:writeme@10.1.5.29:8581/models/test.txt

### VM MOR
Connection string:  
192.168.56.101:8563  

#### EXASolution
https://192.168.56.101/   

#### BucketFS

##### BucketFS Services
bucketfs1
Port: 2580

##### Buckets
`/buckets/bucketfs1/models`  
read PW: `readme`  
write PW: `writeme`

`/buckets/bucketfs1/languages`  
read PW: `readme2`  
write PW: `writeme2`

Example for bucket access:
```bash
echo 'Hello World!' > test.txt
curl -i -X PUT -T test.txt http://w:writeme@192.168.56.101:2580/models/test.txt
rm test.txt
curl -X GET -O http://w:readme@192.168.56.101:2580/models/test.txt
rm test.txt
curl -i -X DELETE http://w:writeme@192.168.56.101:2580/models/test.txt
```

Load client container from exasol
```bash
docker import http://192.168.56.101:2581/default/EXAClusterOS/ScriptLanguages-2018-05-07.tar.gz exa_udf_container 
```

Execute container to built client
```
docker run -v `pwd`/script-languages/python_client:/py --name=exa_udf_container -it exa_udf_container /bin/bash
```

### NLP python
In order to build and deploy NLP flavor python3 to Exasol, navigate to `./script-languages`, build the container with 
 ```bash
 ./build -f python3-nlp-EXASOL-6.1.0
 ```
export image to tar ball 
```bash
./export -f python3-nlp-EXASOL-6.1.0
```
upload to exasol 
```bash
curl -v -X PUT -T python3-nlp-EXASOL-6.0.0.tar.gz http://w:writeme2@192.168.56.101:2580/languages/python3-nlp-EXASOL-6.0.0.tar.gz
```
activate the script language container either in a session
```sql
ALTER SESSION SET SCRIPT_LANGUAGES='PYNLP=localzmq+protobuf:///bucketfs1/languages/python3-nlp-EXASOL-6.0.0?lang=python#buckets/bucketfs1/languages/python3-nlp-EXASOL-6.0.0/exaudf/exaudfclient_py3';
```
or for the whole system
```sql
ALTER SYSTEM SET SCRIPT_LANGUAGES='PYNLP=localzmq+protobuf:///bucketfs1/languages/python3-nlp-EXASOL-6.0.0?lang=python#buckets/bucketfs1/languages/python3-nlp-EXASOL-6.0.0/exaudf/exaudfclient_py3';
```

*Note*: To use UDF's with an elt tool such as Data Chef, you need to set the script language for the system.

## Steam Game Reviews
Antoni Sobkowicz. (2017). Steam Review Dataset (2017) [Data set]. Zenodo. http://doi.org/10.5281/zenodo.1000885

## Sources
https://github.com/EXASOL/pyexasol
https://github.com/exasol/data-science-examples/

Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.