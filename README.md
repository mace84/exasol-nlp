# Exasol Showcase
A showcase illustrating how to use natural language processing methods in an 
Exasol ELT pipeline.

## Exasol config

### Koffer
Connection string:  
10.1.5.29:8563

#### DataChef
http://10.1.5.29:4567   
Usr: admin  
PW: admin  

#### EXASolution
https://10.1.5.29:8443
MOR

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
User: `admin`  
Password: `admin`

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
1. Navigate to `./script-languages`
2. Build the container 
 ```bash
 ./build -f python3-nlp-EXASOL-6.1.0
 ```
3. Export image to tar ball 
```bash
./export -f python3-nlp-EXASOL-6.1.0
```
4. Upload to exasol 
```bash
curl -v -X PUT -T python3-nlp-EXASOL-6.0.0.tar.gz http://w:writeme2@192.168.56.101:2580/languages/python3-nlp-EXASOL-6.0.0.tar.gz
```
5. Activate session in  
```sql
ALTER SESSION SET SCRIPT_LANGUAGES='PYNLP=localzmq+protobuf:///bucketfs1/languages/python3-nlp-EXASOL-6.0.0?lang=python#buckets/bucketfs1/languages/python3-nlp-EXASOL-6.0.0/exaudf/exaudfclient_py3';
```


## Data
(KASANDR Data Set)[http://archive.ics.uci.edu/ml/datasets/KASANDR#]

## Sources
https://github.com/EXASOL/pyexasol
https://github.com/exasol/data-science-examples/

Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.

### Steam Game Reviews
Antoni Sobkowicz. (2017). Steam Review Dataset (2017) [Data set]. Zenodo. http://doi.org/10.5281/zenodo.1000885