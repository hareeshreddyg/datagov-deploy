import sys
import requests
import optparse
import json
import pdb
import datetime

import psycopg2


def get_organization_list(url, source_type):
    '''
           Get list of all organizations in Data.gov
    '''
    organizations = []

    organization_list = requests.get(url + "/api/action/package_search?q=source_type:" + source_type + "&rows=1000")
    organization_list = organization_list.json()['result']['results']

    for organization in organization_list:
        if organization['organization']['name'] not in organizations:
            organizations.append(organization['organization']['name'])

    with open('out.txt', 'w') as f:
        print >> f, 'Filename:', organizations

    return organizations


def get_dataset_names(url):
    dataset_names = []
    package_list = []
    start = 0

    # get total number of datasets
    package_list_tmp = requests.post(url + "/api/action/package_list")
    no_datasets = package_list_tmp.json()['result']['count']
    print 'Total number of datasets: ', str(no_datasets)

    while start <= 10:
        data_dict = {'q': '', 'rows': 100, 'start': start}
        package_list_tmp = requests.post(url + "/api/action/package_search",
                                         json = data_dict)
        package_list += package_list_tmp.json()['result']['results']
        start += 1000

    for package in package_list:
        dataset_names.append(package['name'])
    return dataset_names


def get_datagov_datasets(dataset_name):
    organization_datasets = []
    start = 0

    organization_list_tmp = requests.post("https://catalog.data.gov/api/action/package_search?q=name:"+dataset_name+"*")
    no_datasets = organization_list_tmp.json()['result']['count']
    datasets = organization_list_tmp.json()['result']['results']
    duplicates = []

    for data in datasets:
        if data['name'][-6] == '-':
            duplicates.append(data['name'])

    return duplicates


def get_dataset_list(options, datagov_url, organization_name, harvest_type):
    '''
        Get the datasets on data.gov that we have for the organization
    '''
    organization_datasets = []
    dataset_keep = []
    duplicates = []
    organization_harvest = []
    dataset_harvest_list = []

    organization_list_tmp = requests.get(datagov_url+"/api/action/package_search?q=organization:" + organization_name +
                            "&fq=type:dataset")
    total_datasets = organization_list_tmp.json()['result']['count']

    # get list of harvesters for the organization
    organization_harvest_tmp = requests.get(datagov_url+"/api/action/package_search?q=organization:" + organization_name +
                            "&fq=source_type:" + str(harvest_type) + "&rows=100")
    organization_harvest_tmp = organization_harvest_tmp.json()['result']['results']

    for harvest in organization_harvest_tmp:
        organization_harvest.append(harvest['id'])


    for harvest_id in organization_harvest:
        dataset_list = requests.get(datagov_url +'/api/action/package_search?q=harvest_source_id:' + harvest_id)
        harvest_data_count = dataset_list.json()['result']['count']
        start = 0

        while start <= harvest_data_count:
            dataset_list = requests.get(datagov_url +'/api/action/package_search?q=harvest_source_id:'+harvest_id+'&start='+ str(start) + '&rows=1000')
            dataset_harvest_list += dataset_list.json()['result']['results']
            start += 1000


        for dataset_harvest in dataset_harvest_list:
            organization_datasets.append(dataset_harvest['id'])

        dataset_keep_tmp = harvest_datasets(dataset_harvest_list)
        dataset_keep += dataset_keep_tmp

        duplicates = list(set(organization_datasets) - set(dataset_keep))
        remove_duplicates(options, duplicates)

        with open('organization_datasets_' + harvest_id + '.txt', 'w') as f:
            print >> f, 'Filename:', organization_datasets
        with open('duplicates_datasets_' + harvest_id + '.txt', 'w') as f:
            print >> f, 'Filename:', duplicates
        with open('keep_datasets_' + harvest_id + '.txt', 'w') as f:
            print >> f, 'Filename:', dataset_keep

    return duplicates


def harvest_datasets(dataset_harvest_list):
    dataset_keep = []

    for dataset in dataset_harvest_list:
        try:
            for extra in dataset['extras']:
                # get the harvest_id
                oldest_id = dataset['id']

                if extra['key'] == 'identifier':
                    identifier = extra['value']
                    dataset_list = requests.get(datagov_url +'/api/action/package_search?q=identifier:"' + identifier + '"' +
                        '&fq=type:dataset&sort=metadata_modified+asc&rows=100')
                    if dataset_list.status_code == 200:
                        try:
                            dataset_count = dataset_list.json()['result']['count']
                            print dataset_count
                            data = dataset_list.json()['result']['results']

                            if dataset_count > 1:
                                if data[dataset_count-1]['id'] not in dataset_keep:
                                    dataset_keep.append(data[dataset_count-1]['id'])
                            else:
                                dataset_keep.append(dataset['id'])
                        except IndexError:
                            continue

                if extra['key'] == 'extras_rollup':
                    extras_rollup = extra['value']
                    extras_rollup = json.loads(str(extras_rollup))
                    identifier = extras_rollup['identifier']

                    dataset_list = requests.get(datagov_url +'/api/action/package_search?q=identifier:"' + identifier + '"' +
                                    '&fq=type:dataset&sort=metadata_modified+asc&rows=1000')
                    if dataset_list.status_code == 200:
                        dataset_count = dataset_list.json()['result']['count']
                        data = dataset_list.json()['result']['results']

                        if dataset_count > 1:
                            if data[dataset_count-1]['id'] not in dataset_keep:
                                dataset_keep.append(data[dataset_count-1]['id'])
                        else:
                            dataset_keep.append(dataset['id'])
        except KeyError:
            continue

    return dataset_keep


def remove_duplicates(options, duplicates):

    conn_string = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(options.db_hostname, options.db_name, options.db_user, options.db_password)
    print "Connecting to database\n ->%s" % (conn_string)

    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    for data in duplicates:
        print data
        cursor.execute("update package set state='deleted' where id='" + data + "';")
        conn.commit()

    conn.close()


if __name__ == "__main__":
    '''
        Only the code for getting the list of organizations and
        the code for getting all the datasets for the organization will run
        In the end we'll have files with the names of the datasets that need
        to be deleted and the ones that have to stay
    '''
    optlist = [
        # use capitalized versions of std options help and version
        optparse.make_option("-h", "--help",
                             action="help",
                             help="Show this help message and exit"),
        optparse.make_option("-H", "--db-hostname",
                             dest="db_hostname",
                             help="Hostname of db"),
        optparse.make_option("-n", "--db-name",
                             dest="db_name",
                             help="Name of database"),
        optparse.make_option("-u", "--db-user",
                             dest="db_user",
                             help="Database login user."),
        optparse.make_option("-p", "--db-password",
                             dest="db_password",
                             help="Database login password."),
        optparse.make_option("-l", "--datagov-url",
                             dest="datagov_url",
                             help="URL to data gov site."),
        optparse.make_option("-k", "--sysadmin-api-key",
                             dest="sysadmin_api_key",
                             help="API key for sysadmin.")
        ]

    optparse.OptionParser()
    optparser = optparse.OptionParser(None, add_help_option=False)
    optparser.add_options(optlist)

    (o, args) = optparser.parse_args()

    datagov_url = o.datagov_url
    sysadmin_api_key = o.sysadmin_api_key
    datagov_datasets = []
    organization_harvest_list = []

    # get organizations that have datajson harvester
    organization_list = get_organization_list(datagov_url, 'datajson')
    print organization_list

    # get list of duplicates
    for organization in organization_list:
        duplicates = get_dataset_list(o, datagov_url, organization, 'datajson')
        # remove duplicates
        #remove_duplicates(duplicates, sysadmin_api_key)
