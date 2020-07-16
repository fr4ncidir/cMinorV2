# How to use cMinor v2

Hello! If you are reading this, it's very likely that you want to use cMinor version 2.

The software has been slightly modified since the previous version that was described in [this](https://ieeexplore.ieee.org/abstract/document/8588087) paper:

Viola, F., Turchet, L., Antoniazzi,
F., & Fazekas, G. (2018, November). C minor: a semantic
publish/subscribe broker for the internet of musical things. In *2018 23rd Conference of Open Innovations Association (FRUCT)* (pp. 405-415). IEEE.

So, let's start here to use **cMinor v2**.

## 1. First things to do

The most stable version of cMinor v2 will be stored in [this](https://gitlab.emse.fr/francesco.antoniazzi/cminor-emse) repository, at _master_ branch.
So, the first thing to do is

```
$ git clone https://gitlab.emse.fr/francesco.antoniazzi/cminor-emse.git
```

The second thing that would be wise to do is to create a Python3 virtual environment. This is not compulsory, but yet highly recommended. This is usually done this way

```
$ cd 'your_folder'
$ virtualenv -p python3 ./venv
$ source ./venv/bin/activate
```

At this point, your Python3 virtual environment is activated, and we can proceed with cMinor.

## 2. Installing requirements

There should be a `requirements.txt` file in the repository. So, to install every required library, you should type

```
$ pip3 install -r requirements.txt
```

We are now ready to run cMinor v2.

## 3. Running cMinor v2

First of all, since cMinor works with an RDF store, you have to decide if to run Blazegraph, or to use rdflib to store your triples. If you want to use Blazegraph, go to section 3.1; otherwise, section 3.2 for rdflib.

#### 3.1 cMinor over a Blazegraph endpoint

Of course, you must run a Blazegraph instance. Please refer to [Blazegraph website](https://blazegraph.com/) to know how to do this.

Once this is done, the first thing to try is:

```
$ python3 cminor.py --help
```

You should now see some helpful information that would help you to understand the following call, that is meant to be _the standard way to call cMinor v2_ (i.e., with a blazegraph RDF endpoint running, and listening on localhost.

```
$ python3 cminor.py 
```

#### 3.2 cMinor on a rdflib endpoint

There is nothing to install in this case. The drawback of using rdflib is that cMinor doesn't provide a way to store permanently triples when we use rdflib. This means that if you close cMinor, you lose your knowledge base.

```
$ python cminor.py --endpoint rdflib
```

## 4. Using cMinor

The interaction with cMinor can be of 3 different types:

- Query
- Update
- Subscribe

#### 4.1 Query

As it is done with any SPARQL RDF endpoint, e.g. Blazegraph, you can use the SPARQL language to issue a query to cMinor. Since cMinor can be contacted through CoAP protocol, you need to build a CoAP request like the following, depending of course on your host setup.

```
COAP GET
Host: coap://localhost/sparql/query

Payload:
SELECT * WHERE {
    ?a ?b ?c
}
```

The response payload will contain the bindings of the result, or an error code.

#### 4.2 Update

You can use the SPARQL language to issue an update to cMinor. Since cMinor can be contacted through CoAP protocol, you need to build a CoAP request like the following, depending of course on your host setup.

```
COAP POST
Host: coap://localhost/sparql/update

Payload:
PREFIX : <http://cMinor/Example#>
INSERT DATA {
   :subject :predicate :object.
}
```

The response payload may contain some result. However, it always contains a success (or error) code.

Notice that it is also possible to make an update like the following:

```
COAP POST
Host: coap://localhost/sparql/update?format=ttl

Payload:
@prefix : <http://cMinor/Example#>
:subject :predicate :object.
```

Issuing in this way a request on a turtle (or n3, or rdf/xml) file, instead that with SPARQL.

#### 4.3 Subscribe

The subscription creation is a two step procedure: (i) creation of the subscription resource; (ii) observation of the resource.

##### _4.3.1 Creation of the resource_

To create a subscription in cMinor, you have to issue a request like the following:

```
COAP POST
Host: coap://localhost/sparql/subscription

Payload:
SELECT * WHERE {
   ?a ?b ?c
}
```

Once this request is received, cMinor creates a new subscription resource that is reachable at `coap://localhost/{payload_hash}`. Such hash will be returned back to the client within the payload. So, if the payload is `SELECT * WHERE {?a ?b ?c}`, the created resource will be located at `coap://localhost/11354c8e688bcd6f6da34c6293be8cac`. In this way, if two clients issue an identical subscription, they just end up in being addressed to observe the same resource.

##### _4.3.1 Observe the resource_

Once you are ready, you can observe the resource `coap://localhost/11354c8e688bcd6f6da34c6293be8cac` with your coap APIs and be notified about events.

What are these events? Let's identify some examples.

1. Let's imagine that the RDF store is empty at the beginning. We (CLIENT1) request a subscription like the one in 4.3.1 `SELECT * WHERE {?a ?b ?c}`. We then start the observation.

Another client (CLIENT2) now makes an update like the following:

```
COAP POST
Host: coap://localhost/sparql/update

Payload:
PREFIX : <http://cMinor/Example#>
INSERT DATA {
   :subject :predicate :object.
}
```

CLIENT1 will now be notified that something happened. In particular, the subscription query `SELECT * WHERE {?a ?b ?c}` is made by cMinor _before_ and _after_ the update. Since the two results are different, (before=`empty`, after=`{a=:subject, b=:predicate, c=:object}`, the contents of _after_ is sent as a notification to the client.

This means that if nothing changes, no notification is issued.

2. If CLIENT2 makes another update:

```
COAP POST
Host: coap://localhost/sparql/update

Payload:
PREFIX : <http://cMinor/Example#>
INSERT DATA {
   :sub :pred :obj.
}
```

Since the two results are different, (before=`{a=:subject, b=:predicate, c=:object}`, after=`{[a=:subject, b=:predicate, c=:object], [a=:sub, b=:pred, c=:obj]}`, the contents of _after_ is sent as a notification to the client.

Notice that there is here the great difference with SEPA implementations: we don't retransmit added/removed bindings: we just retransmit the whole query result.

## 5. The cCoap tool

cCoap is a script that easily makes CoAP calls for cMinor. So, if you want to make a query:

```
$ python3 cCoap.py -a coap://localhost/sparql/query -p "SELECT * WHERE {?a ?b ?c}"
```

If you want to make an update:

```
$ python3 cCoap.py -a coap://localhost/sparql/update -p "PREFIX : <http://cMinor/Example#> INSERT DATA {:sub :pred :obj}" --verb POST
```

If you want to make a subscription request:

```
$ python3 cCoap.py -a coap://localhost/sparql/subscription -p "SELECT * WHERE {?a ?b ?c}" --verb POST
```

If you want to observe the subscription resource:

```
$ python3 cCoap.py -a coap://localhost/11354c8e688bcd6f6da34c6293be8cac -o
```

If you need to create your own cMinor client, you will probably start by having a look to the cCoap.py source code.

##### Authors:

[Francesco Antoniazzi](mailto:francesco.antoniazzi@emse.fr)

[Jehad Melad](jehad.melad@emse.fr)
