from background_task import background

# generic imports 
import time
import uuid

# Get an instance of a logger
import logging
logger = logging.getLogger(__name__)

from core import models as models

'''
This file provides background tasks that are performed with Django-Background-Tasks
'''

@background(schedule=1)
def delete_model_instance(instance_model, instance_id, verbose_name=uuid.uuid4().urn):

	'''
	Background task to delete generic DB model instance
	'''
	
	# try:

	# get model		
	m = getattr(models, instance_model, None)

	if m:

		# get model instance
		i = m.objects.get(pk=int(instance_id))
		logger.debug('retrieved %s model, instance ID %s, deleting' % (m.__name__, instance_id))
	
		# delete		
		return i.delete()

	else:
		logger.debug('Combine model %s not found, aborting' % (instance_model))	


@background(schedule=1)
def download_and_index_bulk_data(dbdd_id, verbose_name=uuid.uuid4().urn):

	'''
	Background task driver to manage downloading and indexing of bulk data

	Args:
		dbdd_id (int): ID of DPLABulkDataDownload (dbdd) instance
	'''

	# init bulk download instance
	dbdd = models.DPLABulkDataDownload.objects.get(pk=dbdd_id)

	# init data client with filepath
	dbdc = models.DPLABulkDataClient()

	# download data
	logger.debug('downloading %s' % dbdd.s3_key)
	dbdd.status = 'downloading'
	dbdd.save()
	download_results = dbdc.download_bulk_data(dbdd.s3_key, dbdd.filepath)	

	# index data
	logger.debug('indexing %s' % dbdd.filepath)
	dbdd.status = 'indexing'
	dbdd.save()
	es_index = dbdc.index_to_es(dbdd.s3_key, dbdd.filepath)	

	# update and return
	dbdd.es_index = es_index
	dbdd.status = 'finished'
	dbdd.save()



@background(schedule=1)
def create_validation_report(ct_id):

	'''
	Function to generate a Validation Report for a Job as a bg task

	Args:
		request (django.request): request object with parameters needed for report generation

	Returns:
		location on disk
	'''

	# get CombineTask (ct)

	ct = models.CombineBackgroundTask.objects.get(pk=int(ct_id))
	logger.debug('using %s' % ct)

	# test task params
	logger.debug(ct.task_params)

	# OLD ###################################################################################################
	# logger.debug('generating validation results report')

	# # debug form
	# logger.debug(request.POST)

	# # get job name
	# report_name = request.POST.get('report_name')
	# if report_name == '':
	# 	report_name = 'Validation Report'

	# # get report output format
	# report_format = request.POST.get('report_format')

	# # get requested validation scenarios to include in report
	# validation_scenarios = request.POST.getlist('validation_scenario', [])

	# # get mapped fields to include
	# mapped_field_include = request.POST.getlist('mapped_field_include', [])

	# # run report generation
	# report_output = cjob.generate_validation_report(
	# 		report_format=report_format,
	# 		validation_scenarios=validation_scenarios,
	# 		mapped_field_include=mapped_field_include
	# 	)

	# # response is to download file from disk
	# with open(report_output, 'rb') as fhand:
		
	# 	# csv
	# 	if report_format == 'csv':
	# 		content_type = 'text/plain'
	# 		attachment_filename = '%s.csv' % report_name
		
	# 	# excel
	# 	if report_format == 'excel':
	# 		content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	# 		# content_type = 'text/plain'
	# 		attachment_filename = '%s.xlsx' % report_name

	# 	# prepare and return response
	# 	response = HttpResponse(fhand, content_type=content_type)
	# 	response['Content-Disposition'] = 'attachment; filename="%s"' % attachment_filename
	# 	return response
	# OLD ###################################################################################################



@background(schedule=1)
def test_bg_task(duration=5):

	logger.debug('preparing to sleep for: %s' % duration)
	time.sleep(duration)
	return "we had a good nap"











