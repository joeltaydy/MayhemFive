import os
import boto3
import shlex, subprocess
import Module_DeploymentMonitoring.src.aws_config

#-----------------------------------------------------------------------------#
#----------------------------- AWS Functions ---------------------------------#
#-----------------------------------------------------------------------------#

# Return output : tuple, error : default-None
def executeBash(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    return process.communicate()


# Return True is pk is added. ELSE raise Exception
def addPublicKey(username=None,public_key=None):
    if username == None or public_key == None:
        raise Exception('Please define a username and a public key')

    if 'ssh-rsa' not in public_key:
        public_key = 'ssh-rsa ' + public_key

    pk_dir = '/home/' + username + '/.ssh/authorized_keys'
    bashCommand = 'sudo bash -c "echo # ' + username + ' public key >> ' + pk_dir + '"'
    bashCommand_1 = 'sudo bash -c "echo ' + public_key + ' >> ' + pk_dir + '"'

    try:
        subprocess.Popen(shlex.split(bashCommand), stdout=subprocess.PIPE)
        subprocess.Popen(shlex.split(bashCommand_1), stdout=subprocess.PIPE)
    except:
        raise Exception('Unable to add public key for user ' + username)

    return {'status':True,'message':'Successfully create and added public key into account'}


# Return True is user is create. ELSE raise Exception
def addUser(username=None,public_key=None):
    if username == None:
        raise Exception('Please define a username for the new user')

    try:
        bashCommand = 'sudo adduser ' + username
        executeBash(bashCommand)
    except:
        raise Exception('User ' + username + ' already exists')

    # ========================= Create .ssh folder ========================== #

    bashCommand = 'sudo mkdir /home/' + username + '/.ssh'
    executeBash(bashCommand)

    bashCommand = 'sudo chown ' + username + ':' + username + ' /home/' + username + '/.ssh'
    executeBash(bashCommand)

    bashCommand = 'sudo chmod 700 /home/' + username + '/.ssh'
    executeBash(bashCommand)

    # ===================== Create authorized_keys file ===================== #

    bashCommand = 'sudo touch /home/' + username + '/.ssh/authorized_keys'
    executeBash(bashCommand)

    bashCommand = 'sudo chown ' + username + ':' + username + ' /home/' + username + '/.ssh/authorized_keys'
    executeBash(bashCommand)

    bashCommand = 'sudo chmod 600 /home/' + username + '/.ssh/authorized_keys'
    executeBash(bashCommand)

    # ============================ Add public key =========================== #

    if public_key != None:
        return addPublicKey(username,public_key)

    return {'status':True,'message':'Successfully create a user account'}


# Return output : tuple, error : default-None
def delUser(username=None):
    if username == None:
        raise Exception('Please define a user to delete')

    bashCommand = 'sudo userdel -r ' + username
    executeBash(bashCommand)

    return {'status':True,'message':'Successfully deleted user account'}


# Return public key : String
def generateKeyPair(username=None):
    if username == None:
        raise Exception('Please define a username')

    ec2 = boto3.client('ec2')
    try:
        response = ec2.create_key_pair(KeyName=username)
    except:
        results = delAWSKeyPair(username)
        if results['status']:
            response = ec2.create_key_pair(KeyName=username)
        else:
            raise Exception(results['message'])

    private_key = response['KeyMaterial']
    key_name = response['KeyName']

    file_path = os.path.join(aws_config.OUTPUT_FOLDER,key_name+'.pem')
    result = writeKeyPairFile(private_key,file_path)

    return {'key_name':key_name,'private_key':private_key,'public_key':getPublicKey(username,file_path).decode('utf-8').strip()}


# Return public key : String
def getPublicKey(username=None,file_name=None,file_path=None):
    if username == None and file_name == None and file_path == None:
        raise Exception('Please define a username, file name or a file path')

    file_name = username + '.pem' if username != None else file_name
    file_path = os.path.join(aws_config.OUTPUT_FOLDER,file_name) if file_name != None else file_path

    bashCommand = 'sudo ssh-keygen -y -f "' + file_path + '"'
    output,error = subprocess.Popen(shlex.split(bashCommand), stdout=subprocess.PIPE).communicate()

    return output


# Return True is successful delete. ELSE False
def delKeyPairFile(username=None,file_name=None,file_path=None,):
    if username == None and file_name == None and file_path == None:
        raise Exception('Please define a username, file name or a file path')

    file_name = username + '.pem' if username != None else file_name
    file_path = os.path.join(aws_config.OUTPUT_FOLDER,file_name) if file_name != None else file_path

    try:
        os.remove(file_path)
    except:
        return {'status':False,'message':file_path + ' does not exists'}

    return {'status':True,'message':None}


# Return True is successful write. ELSE False
def writeKeyPairFile(private_key=None,file_path=None):
    try:
        with open(file_path,'w') as file:
            file.write(private_key)
    except Exception as e:
        return {'status':False,'message':e.args[0]}

    return {'status':True,'message':None}


# Return True is successful delete. ELSE False
def delAWSKeyPair(username=None):
    if username == None:
        raise Exception('Please define a username')

    try:
        ec2 = boto3.client('ec2')
        response = ec2.delete_key_pair(KeyName=username)
    except Exception as e:
        return {'status':False,'message':e.args[0]}

    return {'status':True,'message':None}


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


if __name__ == "__main__":
    # Run test commands here
    aws_config.OUTPUT_FOLDER = os.path.join(os.getcwd(),'private_keys')
    username = 'Test'
