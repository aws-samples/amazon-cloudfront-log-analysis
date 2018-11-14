'use strict';

const AWS = require('aws-sdk');
const firehose = new AWS.Firehose({region: '<kineis-firehose-region>'});

const streamName = "<kineis-firehose-delivery-stream>"
console.log("StreamName: ", streamName);

function parseRequest(eventData) {
    
    var parsedJson = {};
    
    parsedJson.executionRegion = process.env.AWS_REGION;
    parsedJson.requestId = null;
    parsedJson.distributionId = eventData.config.distributionId;
    parsedJson.distributionName = eventData.config.distributionDomainName;
    parsedJson.eventType = eventData.config.eventType;
    parsedJson.customTraceId = null;
    parsedJson.viewerCountry = "unknown";
    parsedJson.deviceFormFactor = "unknown";
    
    if(eventData.request.headers["x-request-id"]) { //check if the custom header exists
      parsedJson.requestId = eventData.request.headers["x-request-id"][0].value;
    }
    
    if(eventData.request.headers["x-my-trace-id"]) { //check if the custom header exists, this is added as part of client side instrumentation
      parsedJson.customTraceId = eventData.request.headers["x-my-trace-id"][0].value;
    }
    
    if(eventData.request.headers["cloudfront-viewer-country"]) { //check if the custom header exists, this is added by Amazon CloudFront if the headers are whitelisted
      parsedJson.viewerCountry = eventData.request.headers["cloudfront-viewer-country"][0].value;
    }
    
    if(eventData.request.headers["cloudfront-is-mobile-viewer"] && eventData.request.headers["cloudfront-is-mobile-viewer"][0].value == 'true') { //check if the custom header exists, this is added by Amazon CloudFront if the headers are whitelisted
      parsedJson.deviceFormFactor = "mobile";
    } else if (eventData.request.headers["cloudfront-is-tablet-viewer"] && eventData.request.headers["cloudfront-is-tablet-viewer"][0].value == 'true') {
      parsedJson.deviceFormFactor = "tablet";
    } else if (eventData.request.headers["cloudfront-is-smarttv-viewer"] && eventData.request.headers["cloudfront-is-smarttv-viewer"][0].value == 'true') {
      parsedJson.deviceFormFactor = "smarttv";
    } else if (eventData.request.headers["cloudfront-is-desktop-viewer"] && eventData.request.headers["cloudfront-is-desktop-viewer"][0].value == 'true') {
      parsedJson.deviceFormFactor = "desktop";
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
    
    const request = event.Records[0].cf.request;
    
    const parsedRequestJson = parseRequest(event.Records[0].cf);
    sendToKinesisFirehose(parsedRequestJson, streamName);
    
    //Rejecting requests from EU(Frankfurt) with viewer country code = 'DE'
    if(parsedRequestJson.viewerCountry == 'DE' ){
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
    }
    else {
      callback(null, request);  
    }
};