import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

################################################################################################################## 
# VIEWER REQUEST LAMBDA@EDGE LOGS - Conversion from JSon to Parquet format partitioned by year, month, date hour #
##################################################################################################################
## Create dyanmaic frame from raw(Json format) viewer request Lambda@Edge logs as the datasource. Glue Data Catalog = {database = "reInvent2018_aws_service_logs", table_name = "le_log_raw_viewer_request"} 
viewerRequestLELog = glueContext.create_dynamic_frame.from_catalog(database = "reInvent2018_aws_service_logs", table_name = "le_log_raw_viewer_request", transformation_ctx = "viewerRequestLELog")

## Map the viewer request Lambda@Edge logs to target format
mappedViewerRequestLELog = ApplyMapping.apply(frame = viewerRequestLELog, mappings = [("executionregion", "string", "executionregion", "string"), ("requestid", "string", "requestid", "string"), ("distributionid", "string", "distributionid", "string"), ("distributionname", "string", "distributionname", "string"), ("eventtype", "string", "eventtype", "string"), ("requestdata", "string", "requestdata", "string"), ("customtraceid", "string", "customtraceid", "string"), ("useragentstring", "string", "useragentstring", "string"), ("partition_0", "string", "year", "string"), ("partition_1", "string", "month", "string"), ("partition_2", "string", "date", "string"), ("partition_3", "string", "hour", "string")], transformation_ctx = "mappedViewerRequestLELog")

## Resolves a choice type within a DynamicFrame
resolvedViewerRequestLELog = ResolveChoice.apply(frame = mappedViewerRequestLELog, choice = "make_struct", transformation_ctx = "resolvedViewerRequestLELog")

## Drops all null fields in a DynamicFrame whose type is NullType
cleanedViewerRequestLELog = DropNullFields.apply(frame = resolvedViewerRequestLELog, transformation_ctx = "cleanedViewerRequestLELog")

## Write the viewer request Lambda@Edge logs to the S3 path(s3://cf-log-bucket-lab/converted/lelogs/viewer-request) in the optimized (Parquet) format partitioned by year, month, date hour
viewerRequestLELogSink = glueContext.write_dynamic_frame.from_options(frame = cleanedViewerRequestLELog, connection_type = "s3", connection_options = {"path": "s3://us-east-1.data-analytics/cflogworkshop/optimized/lelogs/viewer-request", "partitionKeys": ["year", "month", "date", "hour"]}, format = "parquet", transformation_ctx = "viewerRequestLELogSink")


################################################################################################################## 
# ORIGIN REQUEST LAMBDA@EDGE LOGS - Conversion from JSon to Parquet format partitioned by year, month, date hour #
##################################################################################################################
## Create dyanmaic frame from raw(Json format) origin request Lambda@Edge logs as the datasource. Glue Data Catalog = {database = "reInvent2018_aws_service_logs", table_name = "le_log_raw_origin_request"} 
originRequestLELog = glueContext.create_dynamic_frame.from_catalog(database = "reInvent2018_aws_service_logs", table_name = "le_log_raw_origin_request", transformation_ctx = "originRequestLELog")

## Map the origin request Lambda@Edge logs to target format
mappedOriginRequestLELog = ApplyMapping.apply(frame = originRequestLELog, mappings = [("executionregion", "string", "executionregion", "string"), ("requestid", "string", "requestid", "string"), ("distributionid", "string", "distributionid", "string"), ("distributionname", "string", "distributionname", "string"), ("eventtype", "string", "eventtype", "string"), ("requestdata", "string", "requestdata", "string"), ("viewercountry", "string", "viewercountry", "string"), ("deviceformfactor", "string", "deviceformfactor", "string"), ("customtraceid", "string", "customtraceid", "string"), ("partition_0", "string", "year", "string"), ("partition_1", "string", "month", "string"), ("partition_2", "string", "date", "string"), ("partition_3", "string", "hour", "string")], transformation_ctx = "mappedOriginRequestLELog")

## Resolves a choice type within a DynamicFrame
resolvedOriginRequestLELog = ResolveChoice.apply(frame = mappedOriginRequestLELog, choice = "make_struct", transformation_ctx = "resolvedOriginRequestLELog")

## Drops all null fields in a DynamicFrame whose type is NullType
cleanedOriginRequestLELog = DropNullFields.apply(frame = resolvedOriginRequestLELog, transformation_ctx = "cleanedOriginRequestLELog")

## Write the origin request Lambda@Edge logs to the S3 path(s3://cf-log-bucket-lab/converted/lelogs/origin-request) in the optimized (Parquet) format partitioned by year, month, date hour
originRequestLELogSink = glueContext.write_dynamic_frame.from_options(frame = cleanedOriginRequestLELog, connection_type = "s3", connection_options = {"path": "s3://us-east-1.data-analytics/cflogworkshop/optimized/lelogs/origin-request", "partitionKeys": ["year", "month", "date", "hour"]}, format = "parquet", transformation_ctx = "originRequestLELogSink")

job.commit()