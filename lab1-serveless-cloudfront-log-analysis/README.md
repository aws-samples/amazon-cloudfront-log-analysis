# LAB 1: Serverless Amazon CloudFront Log Analysis Pipeline

## Overview

## Architecture Diagram

![architecture-overview.png](./assets/architecture-diagram.png)


## Create AWS IAM Role

Create an IAM role that has permission to your Amazon S3 sources, targets, temporary directory, scripts, AWSGlueServiceRole and any libraries used by the job.

- Open the AWS Management console for AWS IAM from [here](https://console.aws.amazon.com/iam/home?region=us-west-2#/roles)
- On the IAM **Role** page click on **Create role**
- Choose **Glue** under **Choose the service that will use this role section**
- Ensure that **Glue** is shown under the **Select your use case** section 
- Click on **Next:Permissions** on the bottom
- On the Attach permissions policies, search policies for S3 and check the box for **AmazonS3FullAccess**

> **Note**: Do not click on the policy, you just have to check the corresponding checkbox

- On the same page, now search policies for Glue and check the box for *AWSGlueConsoleFullAccess* and *AWSGlueServiceRole*.

> **Note**: Do not click on the policy, you just have to check the corresponding checkbox

- Click on **Next:Review**
- Type the **Role name** *(e.g. ReInvent2018-CTD410-GlueRole)*
- Type the **Role description** (optional)
- Ensure that **AmazonS3FullAccess**, **AWSGlueConsoleFullAccess** and **AWSGlueServiceRole** are listed under policies
- Click **Create role**

## Create AWS Glue ETL Job

- Open the AWS Management console for AWS Glue service from [here](https://eu-west-1.console.aws.amazon.com/glue/home?region=eu-west-1)
- If this is your first time visiting the AWS Management Console for AWS Glue, you will get a Getting Started page. Choose **Get Started**. If this isn't your first time, the **Tables** pages opens.
- Make a note of the AWS region name, for example, for this lab you will need to choose the *eu-west-1 (Ireland) *region
- Click on **Jobs** under the *ETL *section in the navigation pane on the left
- Click on **Add job** to create a new ETL job to join the Amazon CloudFront access logs, Lambda@Edge(viewer-request and origin-request) logs and Application Load Balancer logs
- On the **Job properties** page, type the **Name** *(e.g. ReInvent2018-CTD410-LogCombiner)* of the AWS Glue ETL job
- Choose the **IAM role** you created *(e.g. ReInvent2018-CTD410-GlueRole)* as part of the previous section in this lab from the drop down menu
- Select **A new script to be authored by you** for **This job runs**
- Select **Python** as the **ETL language**
- Click **Next**
- On the **Connections** page, click **Next**
- On the **Review** page, click **Save job and edit script**
- If this your first time, a **Script editor tips** page will pop up. Close the pop up page by clicking on the *x *symbol on the top right
- Copy and paste the LogCombiner script [log-combiner-glue-script.py](./log-combiner-glue-script.py) to AWS Glue script editor pane
- Replace the place holder *<your-s3-bucket>* with the name of the Amazon S3 bucket your created at the beginning of this lab

> **Note:** This step may take from upto 15 minutes to complete. 

- Click **Save**
- Click **Run**
- Click **Run job** on the popped up **Parameters(optional)** page
- Close the script editor page by click on **X** symbol on the right hand side of the page 
- On the Jobs pages check the box next to the name of the Glue ETL job *(e.g. ReInvent2018-CTD410-LogCombiner)* *to view the current status of the job under the **History** tab at the bottom of the page
- Ensure that the *Run status *is displaced as **Running**
- Wait until the Run status changes to **Succeeded** 

> **Note:** This step may take from upto 15 minutes to complete.

## License Summary

This sample code is made available under a modified MIT license. See the LICENSE file.