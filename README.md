# Analyze & Visualize Amazon CloudFront and Lambda@Edge Logs to Improve Customer Experience on your Website.

## Overview

Nowadays, web servers are often fronted by a global content delivery network, such as Amazon CloudFront, to accelerate delivery of websites, APIs, media content, and other web assets. In this hands-on-workshop, learn to improve website availability, optimize content based on devices, browser and user demographics, identify and analyze CDN usage patterns, and perform end-to-end debugging by correlating logs from various points in a request-response pipeline. Build an end-to-end serverless solution to analyze Amazon CloudFront logs using AWS Glue and Amazon Athena, generate visualization to derive deeper insights using Amazon QuickSight, and correlate with other logs such Lambda@Edge logs, ALB logs to provide finer debugging experiences. You will also learn how to use the popular ELK(Elasticsearch,Logstash,Kibana) solution for geospatial visualization of CloudFront logs. Discuss how you can extend the pipeline you just built to generate deeper insights needed to improve the overall experience for your users.

## AWS Console

### Verifying your region in the AWS Management Console

With Amazon Ec2, you can place instances in multiple locations. Amazon EC2 locations are composed of regions that contain more that one Availability Zones. Regions are dispersed and located in separate geographic areas (US, EU, etc.). Availability Zones are distinct locations within a region. They are are engineered to be isolated from failures in other Availability Zones and to provide inexpensive, low-latency network connectivity to other Availability Zones in the same region.

By launching instances in separate regions, you can design your application to be closer to specific customers or to meet legal or other requirements. By launching instances in separate Availability Zones, you can protect your application from localized regional failures.

### Verify your Region

The AWS region name is always listed in the upper-right corner of the AWS Management Console, in the navigation bar.

* Make a note of the AWS region name, for example, for this lab you will need to choose the **EU West-1 (Ireland)** region.
* Use the chart below to determine the region code. Choose **eu-west-1 for this lab.**

| Region Name |Region Code|
|---|---|
|US East (Northern Virginia) Region|us-east-1  |
|US West (Oregon) Region|us-west-2|
|Asia Pacific (Tokyo) Region|ap-northeast-1|
|Asia Pacific (Seoul) Region|ap-northeast-2|
|Asia Pacific (Singapore) Region|ap-southeast-1|
|Asia Pacific (Sydney) Region|ap-southeast-2|
|EU (Ireland) Region|eu-west-1|
|EU (Frankfurt) Region|eu-central-1|

---
## Labs

### Pre-requisites
You should have active AWS account with Administrator IAM role
 
|Lab|Name|
|---|----|
|Lab 1|[Serverless Amazon CloudFront Log Analysis Pipeline](./lab1-serveless-cloudfront-log-analysis)|
|Lab 2|[Amazon CloudFront Log Analysis using ELK](./lab2-elk-cloudfront-log-analysis)|

## License Summary

This sample code is made available under a modified MIT license. See the LICENSE file.
