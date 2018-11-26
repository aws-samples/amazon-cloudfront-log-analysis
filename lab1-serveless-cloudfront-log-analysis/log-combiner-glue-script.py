import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import split
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'target_s3_bucket'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

################################################################
# Combining Lambda@Edge Logs -[origin-request, viewer-request] #
################################################################

## Create dyanmaic frame from optimized(Parquet format) Amazon Lambda@Edge viewer request logs as the datasource. Glue Data Catalog = {database = "reInvent2018_aws_service_logs", table_name = "lambdaedge_logs_viewer_request_optimized"}
labdaEdgeViewerRequestLogs = glueContext.create_dynamic_frame.from_catalog(database = "reInvent2018_aws_service_logs", table_name = "lambdaedge_logs_viewer_request_optimized", transformation_ctx = "labdaEdgeViewerRequest")

## Drop the fields that are duplicate between Lambda@Edge viewer request logs and Lambda@Edge origin request logs
modifiedLEViewerRequestLogs = DropFields.apply(frame = labdaEdgeViewerRequestLogs, paths=["eventtype"], transformation_ctx ="modifiedLEViewerRequestLogs")

## Create dyanmaic frame from optimized(Parquet format) Amazon Lambda@Edge origin request logs as the datasource. Glue Data Catalog = {database = "reInvent2018_aws_service_logs", table_name = "lambdaedge_logs_viewer_origin_optimized"}
labdaEdgeOriginRequestLogs = glueContext.create_dynamic_frame.from_catalog(database = "reInvent2018_aws_service_logs", table_name = "lambdaedge_logs_origin_request_optimized", transformation_ctx = "labdaEdgeOriginRequest")

## Drop the fields that are duplicate between Lambda@Edge viewer request logs and Lambda@Edge origin request logs
trimmedLEOriginRequestLogs = DropFields.apply(frame = labdaEdgeOriginRequestLogs, paths=["executionregion", "distributionid", "distributionname", "requestdata", "customtraceid", "eventtype", "year", "month", "date", "hour"], transformation_ctx ="trimmedLEOriginRequestLogs")

## Rename the requestid field for Lambda@Edge origin request logs to origin requestid
modifiedLEOriginRequestLogs = RenameField.apply(frame = trimmedLEOriginRequestLogs, old_name = "requestid", new_name = "origin_requestid", transformation_ctx ="modifiedLEOriginRequestLogs" )

## Convert to DataFrame
modifiedLEOriginRequestLogsDF = modifiedLEOriginRequestLogs.toDF()

## Convert to DataFrame
modifiedLEViewerRequestLogsDF = modifiedLEViewerRequestLogs.toDF()

## Join(left outer join) the Lambda@Edge viewer-request logs with the origin-request logs based on the requestid
combinedLambdaEdgeLogsDF = modifiedLEViewerRequestLogsDF.join(modifiedLEOriginRequestLogsDF, modifiedLEViewerRequestLogsDF["requestid"] == modifiedLEOriginRequestLogsDF["origin_requestid"], "left_outer")

## Convert to DynamicFrame
combinedLambdaEdgeLogs = DynamicFrame.fromDF(combinedLambdaEdgeLogsDF, glueContext, "combinedLambdaEdgeLogs")

## Join the Lambda@Edge viewer-request logs with the origin-request logs based on the requestid
#combinedLambdaEdgeLogs = Join.apply(modifiedLEViewerRequestLogs, modifiedLEOriginRequestLogs, 'requestid', 'origin_requestid')

## Drop the origin_requestid field
lambdaEdgeLogs = DropFields.apply(frame = combinedLambdaEdgeLogs, paths=["origin_requestid"], transformation_ctx ="lambdaEdgeLogs")

## Drop the "year", "month", "date", "hour" fields
trimmedLambdaEdgeLogs = DropFields.apply(frame =lambdaEdgeLogs, paths=["year", "month", "date", "hour", "useragentstring"], transformation_ctx ="trimmedLambdaEdgeLogs")

## Convert to DataFrame
trimmedLambdaEdgeLogsDF = trimmedLambdaEdgeLogs.toDF()

#Destnation S3 loaction for combine Lambda@Edge logs
leLogDestPath = "s3://" + args['target_s3_bucket'] + "/combined/lelogs"

## Write the combined Lambda@Edge logs to S3 (s3://<your-s3-bucket>/combined/lelogs) in optimized Parquet format partitioned by year, month, date, hour
lambdaEdgeLogsSink = glueContext.write_dynamic_frame.from_options(frame = lambdaEdgeLogs, connection_type = "s3", connection_options = {"path": leLogDestPath, "partitionKeys": ["year", "month", "date", "hour"]}, format = "parquet", transformation_ctx = "lambdaEdgeLogsSink")

########################################################################
# Combining Lambda@Edge Logs , CloudFront Access Logs, ALB Access Logs #
########################################################################

## Create dyanmaic frame from optimized(Parquet format) Amazon CloudFront access logs as the datasource. Glue Data Catalog = {database = "reInvent2018_aws_service_logs", table_name = "cf_access_optimized"}
cfLog = glueContext.create_dynamic_frame.from_catalog(database = "reInvent2018_aws_service_logs", table_name = "cf_access_optimized", transformation_ctx = "cfLog")

## Rename the requestid field in the ALB logs to cf_requestid
modifiedCFLogs = RenameField.apply(frame = cfLog, old_name = "requestid", new_name = "cf_requestid", transformation_ctx ="modifiedCFLogs" )

## Convert to DataFrame
modifiedCFLogsDF = modifiedCFLogs.toDF()

## Create dyanmaic frame from optimized(Parquet format) Application Loadbalancer logs as the datasource. Glue Data Catalog = {database = "reInvent2018_aws_service_logs", table_name = "alb_access_optimized"}
albLogs = glueContext.create_dynamic_frame.from_catalog(database = "reInvent2018_aws_service_logs", table_name = "alb_access_optimized", transformation_ctx = "albLog")

## Drop the "year", "month", "day", "hour" fields
trimmedALBLogs = DropFields.apply(frame = albLogs, paths=["year", "month", "day", "hour"], transformation_ctx ="trimmedALBLogs")

## Rename the time field in the ALB logs to alb_time
modifiedALBLogs = RenameField.apply(frame = trimmedALBLogs, old_name = "time", new_name = "alb_time", transformation_ctx ="modifiedALBLogs" )

## Convert ALB Log dynamic frame to Apache Spark data frame
modfiedALBLogDF = modifiedALBLogs.toDF()

## Extract the custom trace id from the albLog coloumn name trace_id in the alb logs, as the Application Load Balancer would have updated the trace_id value with the self field
split_col = split(modfiedALBLogDF['trace_id'], ';')
finalALBLogDF = modfiedALBLogDF.withColumn("custom_trace_id", split_col.getItem(1))

## Join(let outer join) the Lambda@Edge logs with the ALB logs based on the custom trace id
leALBCombinedLogsDF = trimmedLambdaEdgeLogsDF.join(finalALBLogDF, trimmedLambdaEdgeLogsDF["customtraceid"] == finalALBLogDF["custom_trace_id"], "left_outer")

## Join(let outer join) the CloudFront access logs with the combine Lambda@Edge and ALB logs based on the requestid
combinedLogsDF = modifiedCFLogsDF.join(leALBCombinedLogsDF, modifiedCFLogsDF["cf_requestid"] == leALBCombinedLogsDF["requestid"], "left_outer")

## Convert the ALB Log data frame to dynamic frame
combinedLogs = DynamicFrame.fromDF(combinedLogsDF, glueContext, "combinedLogs")

## Drop custom trace id and requestid from combined logs
finalCombinedLogs = DropFields.apply(frame = combinedLogs, paths=["custom_trace_id", "cf_requestid"], transformation_ctx ="finalCombinedLogs")

#Destnation S3 loaction for combine logs
logDestPath = "s3://" + args['target_s3_bucket'] + "/combined/logs"

## Write the combined Lambda@Edge logs to S3 (s3://<your-s3-bucket>/combined/lelogs) in optimized Parquet format partitioned by year, month, day
finalCombinedLogsSink = glueContext.write_dynamic_frame.from_options(frame = finalCombinedLogs, connection_type = "s3", connection_options = {"path": logDestPath, "partitionKeys": ["year", "month", "day"]}, format = "parquet", transformation_ctx = "finalCombinedLogsSink")

job.commit()