'use strict';

const AWS = require('aws-sdk');
const firehose = new AWS.Firehose({region: '<kineis-firehose-region>'});

const streamName = "<kineis-firehose-delivery-stream>";
console.log("StreamName: ", streamName);

function sleep(delayInSeconds) {
  console.log("Adding Delay in Seconds: " + delayInSeconds);
  return new Promise(resolve => setTimeout(resolve, delayInSeconds*1000));
}

function parseRequest(eventData) {
    
    var parsedJson = {};
    
    parsedJson.executionRegion = process.env.AWS_REGION;
    parsedJson.requestId = eventData.config.requestId;
    parsedJson.distributionId = eventData.config.distributionId;
    parsedJson.distributionName = eventData.config.distributionDomainName;
    parsedJson.eventType = eventData.config.eventType;
    parsedJson.requestData = null;
    parsedJson.customTraceId = null;
    parsedJson.userAgentString = null;
    
    if(eventData.request.body.data) { //check if the request data is not empty, in case of the GET method this field could be empty
        parsedJson.requestData = Buffer.from(eventData.request.body.data, 'base64').toString();
    }
    
    if(eventData.request.headers["x-my-trace-id"]) { //check if the custom header exists, this is added as part of client side instrumentation
      parsedJson.customTraceId = eventData.request.headers["x-my-trace-id"][0].value;
    }
    
    if(eventData.request.headers["user-agent"]) { //check if the custom header exists, this is added as part of client side instrumentation
      parsedJson.userAgentString = eventData.request.headers["user-agent"][0].value;
    }
    
    console.log("parsed-request : ", JSON.stringify(parsedJson, null, 2));
    
    return parsedJson;
}

function sendToKinesisFirehose(logMsg, stream){
     
    var params = {
      DeliveryStreamName: stream, 
      Record: {
        Data: JSON.stringify(logMsg) + "\n"
      }
    };
    
    firehose.putRecord(params, function(err, data) {
      if (err) console.log(err, err.stack); // an error occurred
      else     console.log(data);           // successful response
    });
    
    console.log("firehosed-logmessage : ", JSON.stringify(logMsg, null, 2));
} 

exports.handler = (event, context, callback) => {
    
    console.log("StreamName: ", streamName);
    console.log("request-event: ", JSON.stringify(event, null, 2));
    
    const requestId = event.Records[0].cf.config.requestId;
    const request = event.Records[0].cf.request;
    
    //Adding custom header with the requestId from cloudfront
    request.headers['x-request-id'] = [{
      "key": "x-request-id",
      "value": requestId,
    }];
    
    console.log("modified-request: ", JSON.stringify(request, null, 2));
    
    const parsedRequestJson = parseRequest(event.Records[0].cf);
    
    sendToKinesisFirehose(parsedRequestJson, streamName);
    
    //Adding Edge to Origin Delay
    //if(Math.floor(Math.random() * (4 - 0)) == 0) {
    //   sleep(Math.floor(Math.random() * (3 - 0))); 
    //}
    
    //Rejecting requests based on user agent 
    if(request.headers['user-agent'] &&
      (request.headers['user-agent'][0].value == "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" ||
        request.headers['user-agent'][0].value == "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)")) {
        const response = {
          status: '302',
          statusDescription: 'Found',
          headers: {
            location: [{
                key: 'Location',
                value: 'https://' + parsedRequestJson.distributionName + '/notavailable.html',
            }],
          },
      };
      callback(null, response);
    }else {
      callback(null, request);
    }
};
    