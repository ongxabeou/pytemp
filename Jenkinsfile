pipeline {

    agent {
        node {
            label 'slave2'
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

        stage('Build ENV') {
	      steps {
	        sh 'pip3 install -r requirements.txt'
	      }
	    }

	    stage('App Build') {
            steps {
                 sh 'python3 app.py run &'
            }
        }

	    stage('Test') {
	      steps {
	        sh 'python3 test.py'
	      }
	    }

        stage('Run under background process') {
	      steps {
	        sh 'python3 run.py &'
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