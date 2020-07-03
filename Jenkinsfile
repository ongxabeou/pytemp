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

        stage('Build App') {
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
                junit 'test-reports/*.xml'
            }
            post {
                always {
                    script {
                        def msg = "hệ thống vừa chạy pipeline ${currentBuild.fullDisplayName} lên server"
                        echo msg
                        slackSend channel: env.SLACK_CHANNEL, message: msg
                    }
                }
                success {
                    script {
                        def msg = "đã thành công(success)."
                        echo msg
                        slackSend channel: env.SLACK_CHANNEL, message: msg
                    }
                }
                unstable {
                    script {
                        def msg = "nhưng không ổn đinh(unstable)."
                        echo msg
                        slackSend channel: env.SLACK_CHANNEL, message: msg
                    }

                }
                failure {
                    script {
                        def msg = 'đã thất bại(failed).'
                        echo msg
                        slackSend channel: env.SLACK_CHANNEL, message: msg
                    }
                }
                changed {
                    script {
                        def msg = 'đã cập hệ thống(changed)'
                        echo msg
                        slackSend channel: env.SLACK_CHANNEL, message: msg
                    }
                }
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