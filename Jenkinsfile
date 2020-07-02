pipeline {

    agent {
        node {
            label 'ubuntu_root_slave1'
        }
    }

    options {
        buildDiscarder logRotator(
                    daysToKeepStr: '15',
                    numToKeepStr: '10'
            )
    }

    environment {
        APP_NAME = "PYTEMP"
        APP_ENV  = "DEV"
    }

    stages {

        stage('Cleanup Workspace') {
            steps {
                cleanWs()
                sh """
                echo "Cleaned Up Workspace for ${APP_NAME}"
                ls
                """
            }
        }

        stage('Code Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/master']],
                    userRemoteConfigs: [[url: 'https://github.com/ongxabeou/pytemp.git']]
                ])
            }
        }

        stage('Install Virtualenv') {
            steps {
                sh """
                apt-get update \
                && apt-get install -y software-properties-common curl \
                && add-apt-repository ppa:deadsnakes/ppa \
                && apt-get update \
                && apt-get install -y python3.6 python3.6-venv
                python3.6 -m venv ./venv
                """
            }
        }

        stage('Build ENV') {
	      steps {
	        sh """
	        . ./venv/bin/activate
	        python -V
	        pip -V
	        pip install -r requirements.txt
	        deactivate
	        """
	      }
	    }

	    stage('Run App and Run under background process') {
            steps {
                 sh """
                 . ./venv/bin/activate
                 python app.py run &
                 python run.py &
                 deactivate
                 """
            }
        }

	    stage('Test API') {
	      steps {
              sh """
                 . ./venv/bin/activate
                 python test.py
                 deactivate
                 """
	      }
	    }

        stage('Priting All Global Variables') {
            steps {
                sh """
                env
                """
            }
        }

    }
}