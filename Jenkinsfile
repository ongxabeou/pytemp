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

        stage('install python3.6') {
            steps {
                sh """
                add-apt-repository ppa:deadsnakes/ppa -y
                apt-get update -y
                apt install python3.6 -y
                apt-get install -y python3.6-venv python3.6-dev
                python3.6 -m venv ~/${APP_NAME}_venv
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

        stage('Build ENV') {
	      steps {
	        sh """
	        . ~/${APP_NAME}_venv/bin/activate
	        pip install -r requirements.txt
	        """
	      }
	    }

	    stage('App Build') {
            steps {
                 sh 'python app.py run &'
            }
        }

	    stage('Test') {
	      steps {
	        sh 'python test.py'
	      }
	    }

        stage('Run under background process') {
	      steps {
	        sh 'python run.py &'
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