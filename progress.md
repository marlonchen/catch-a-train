# Progress

## Step 1 - core function

* Create a function that takes a location and finds the nearest SEPTA Regional Rail train station using this data set: https://drive.google.com/file/d/11ZfHYz3w77-aM4ZQnQIxSSdxcGnWcFjA/view?usp=drive_link
  * The return format of the train station must be in GeoJSON.
  * Gives walking directions to the train station.
  * Sends SMS walking directions to a given telephone number if provided.

1. I started with Cursor.  I sent all the questions to Cursor, and it came up with 3 files:
- app.py: with APIs and api key validition with predefined keys in redis, and it put notification logic there, too
- station_finder.py: with a kml parser, logic to find nearest station, geojson (but only for station)
- a kubernetes file, which I didn't use, since I think based on usage pattern
    - it could be very popular, which means that we might need the ability to optimize its performance indepedent from other services in the company;
    - looking for train station sounds like most of traffic might be in day time, maybe especially around meal time?
    - we can start with a serverless function, and as we learn more about traffic pattern, we can switch to k8s if we need

1. Cursor didn't generate a working code, but it gave me a good starting point

1. I broke out external dependencies to adaptors, so that it makes testing easy and code less cluttered

1. I created a unit test to learn how data is structured and flowed

1. It didn't take me quite a while to understand some of the details, miles/meters, (lat, lon) and sometime (lon, lat), geojson, and etc.  Sometimes, I fed some questions to ChatGpt, Grok, Claude and DeepSeek, trying to learn faster. 

1. I haven't got the direction instructions working yet.  Still need to look into `project-osrm.org` 

## Setp 2, 3 - REST api

* Build an HTTP API that exposes that function.
* Add authentication to your API.

1. I started with `fastapi`, with predefined API keys in redis, and got it working with redis docker container

1. I created `serverless.yaml` and an aws lambda handler.  I haven't got a chance to work on it.  The purpose is to use lambda initially, when we learn the traffic pattern we can decide later if we need to make a change

1. Also with lambda and api gateway integration, API keys are easier to manage

## Step 4, 5 - cache

* Ensure your API does not search for the same location more than once at a time, even if multiple instances are running concurrently.
* Make your API as cost-effective to operate as possible, given you will charge for each location searched. Explain what factors you took into consideration and what mitigations you put into place.

1. I have redis cache.  Some of data are using python function cache so far, to be changed to redis later.

1. I am not sure at the moment if redis is the right solution.  It is only right because I can finish it faster.  A fansy name is "time to market".  Lol

1. Maybe a dynamodb can be a good candidate for replacement, since it is fast, cheap and supports TTL.

## Step 6 - validation

* Make your API return sensible responses for anyone using from any location in the world. Explain what factors you took into consideration and what improvements you put into place.

1. Checking user's location based on radius

## Step 7 - instance size

* Make your API return sensible responses for anyone using from any location in the world. Explain what factors you took into consideration and what improvements you put into place.

1. I checked DeepSeek and it suggested 3 options: general (m6i.xlarge), compute optimized (c7i.xlarge) and memory optimized (r7i.xlarge).

1. I would pick memory optimized to start with, since we started with redis.  We can lower to general if we choose to use dynamo for caching.  -- maybe a phase 2 user story here

1. other things to consider:
  - use serverless to start with
  - use the services that the company is comfortable to support first

## Step 8 - API protection from malicious users

1. First of all, we will need to create a threat model and identify what we are dealing with
  - We might want to have an API Gateway to handle this concern, since this will probably be common for a lot of external facing services, and we can save a lot of redeployment as the threats are changing.
  - We can use much simpler protection for traffic from API Gateway to the API, and maybe other similar APIs from architecture point of view.
  - Perferrably we can choose from the existing services provided by cloud providers, such as AWS Shield

1. We need to setup enough logging for monitoring and alerts to detect threats and attacks

1. Some of the common threats, such as DDoS
  - AWS Shield might be the first thing to look into, other solutions are available, too.
  - Rate limiting - if an API is leaked and we can stop it early, API Gateway can help operation team to manage the upstream applications
  - Authentication and authorization - it helps manage at user level

1. Some of the best practices, such as
  - keep TLS up-to-date
  - dedicate a team to maintain infrastructure and network security if fundings allow, or outsource the effort 
