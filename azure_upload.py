#!/usr/bin/python
import sys
import getopt
import time
import zipfile
import os

from azure.storage import BlobService
import svn.remote

_opt_svn_repo = 'svn_url'
_opt_svn_user = 'svn_username'
_opt_svn_pass = 'svn_password'
_opt_azure_acc_name = 'azure_acc_name'
_opt_azure_acc_key = 'azure_acc_key'
_opt_azure_container_name = 'azure_container_name'

"""
Exports from an SVN repo, zips it up and uploads it to Azure Blob Storage
"""
def main(argv):
    options = _parse_options(argv)

    blob_service = BlobService(options[_opt_azure_acc_name], options[_opt_azure_acc_key])
    _print_container_names(blob_service)

    blob_service.create_container(options[_opt_azure_container_name])
    _print_blobs(blob_service, options[_opt_azure_container_name])

    export_dir = _export_repo(options)
    export_zip = _zip_export(export_dir)
    _upload_zip(blob_service, options[_opt_azure_container_name], export_zip)

def _parse_options(argv):
    try:
        opts, args = getopt.getopt(argv, '',
                                   map(lambda o: o + '=',
                                       [_opt_svn_repo,
                                        _opt_svn_user,
                                        _opt_svn_pass,
                                        _opt_azure_acc_name,
                                        _opt_azure_acc_key,
                                        _opt_azure_container_name]))
    except getopt.GetoptError:
        print "The following arguments are required:"
        print "--{0}=http://server/path".format(_opt_svn_repo)
        print "--{0}=username".format(_opt_svn_user)
        print "--{0}=password".format(_opt_svn_pass)
        print "--{0}=my_blob_service_acc".format(_opt_azure_acc_name)
        print "--{0}=7r83hgedwehDSfsd==".format(_opt_azure_acc_key)
        print "--{0}=container-name".format(_opt_azure_container_name)
        sys.exit(2)

    # strip off leading '--'
    options = {k[2:]: v for k, v in dict(opts).iteritems()}
    print "Got options: {0}".format(options)

    return options


def _print_container_names(blob_service):
    res = blob_service.list_containers()
    for container in res.containers:
        print "Found container: {0}".format(container.name)


def _print_blobs(blob_service, container_name):
    res = blob_service.list_blobs(container_name)
    for blob in res.blobs:
        print "Found blob: %s" % blob.name


def _export_repo(options):
    r = svn.remote.RemoteClient(options[_opt_svn_repo],
                                username=options[_opt_svn_user],
                                password=options[_opt_svn_pass])
    print "Getting last 3 logs"
    logs = r.log_default(limit=3)
    for log in logs:
        print log
    print "Exporting repo"
    export_dir = '/tmp/export'
    r.export(export_dir)
    print "Repo exported"
    return export_dir


def _zip_export(export_dir):
    # todo fix zip directory relative
    print "Zipping export"
    export_zip = '/tmp/export.zip'
    with zipfile.ZipFile(export_zip, 'w') as zip:
        _zip_directory(export_dir, zip)
    print "Zipped export"
    return export_zip

def _zip_directory(path, zip):
        prefix = len(path)
        for root, dirs, files in os.walk(path):
            for file in files:
                filename = os.path.join(root, file)
                postfix = filename[prefix:]
                print "Got filename {0} and path {1}".format(filename, postfix)
                zip.write(filename, postfix)

def _upload_zip(blob_service, container_name, export_zip):
    print "Uploading zip"
    data = open(export_zip, 'rb').read()
    filename = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
    blob_service.put_blob(container_name, filename + '.zip', data, 'BlockBlob')
    print "Blob uploaded"


if __name__ == "__main__":
    main(sys.argv[1:])
