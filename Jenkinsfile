def getEnvFromBranch(branch) {
  if (branch == 'main') {
    return 'BMA-APP-101'
  } else if (branch == 'test') {
    return 'BMA-APP-701'
  } else {
    return 'BMA-DEV-704'
 }
}
def choosed_agent = getEnvFromBranch(env.BRANCH_NAME)

pipeline {
    agent {
        label "${choosed_agent}"
    }
	options {
      gitLabConnection('gitlab')
      gitlabBuilds(builds: ['Build', 'Test', 'Deploy'])
    }
    stages {
        stage('Build') {
            steps {
                // Get some code from a GitLab repository
                updateGitlabCommitStatus name: 'Build', state: 'pending'
				sh '''
                    . /home/ubuntu/virtual_environments/venv_tms/bin/activate
                    pip install -r requirements.txt
                '''
                updateGitlabCommitStatus name: 'Build', state: 'success'
            }
        }
		stage('Test') {
            steps {
                updateGitlabCommitStatus name: 'Test', state: 'pending'
                sh 'touch lib/config.json'
                sh '''
                    . /home/ubuntu/virtual_environments/venv_tms/bin/activate
                    coverage run --source=. -m pytest
					coverage json --pretty-print --fail-under=100
                '''
            }
			post {
				failure {
					echo "[INFO] Unit Tests failed or code coverage is not 100%"
                    archiveArtifacts artifacts: 'coverage.json'
                    updateGitlabCommitStatus name: 'Test', state: 'failed'
				}
                success {
					archiveArtifacts artifacts: 'coverage.json'
                    updateGitlabCommitStatus name: 'Test', state: 'success'
				}
			}
        }
		stage('Deploy') {
            when { 
                anyOf { 
                    branch 'main'; 
                    branch 'test' 
                } 
            }
            steps {
                updateGitlabCommitStatus name: 'Deploy', state: 'pending'
                sh 'sudo systemctl stop tms.service'
                sh 'sudo rm -rf /opt/tms/'
                sh 'sudo mkdir /opt/tms'
				sh 'sudo mv * /opt/tms'
                sh 'sudo cp /home/ubuntu/.config/tms/config.json /opt/tms/lib/config.json'
                sh 'sudo systemctl start tms.service'
                echo 'New version installed'
                updateGitlabCommitStatus name: 'Deploy', state: 'success'
            }
        }
        stage('Deploy - dev') {
            when { 
                not { 
                    anyOf { 
                        branch 'main'; 
                        branch 'test' 
                    } 
                } 
            }
            steps {
                updateGitlabCommitStatus name: 'Deploy', state: 'pending'
                echo 'Inform GitLab pipeline about status of dev build'
                updateGitlabCommitStatus name: 'Deploy', state: 'success'
            }
        }
    }
	post {
        always {
            cleanWs deleteDirs: true, notFailBuild: true
        }
		failure{			
			emailext body: "Job Failed<br>URL: ${env.BUILD_URL}", 
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']],
					subject: "Job: ${env.JOB_NAME}, Build: #${env.BUILD_NUMBER} - Failure !",
					attachLog: true
        }
        success{			
			emailext body: "Job builded<br>URL: ${env.BUILD_URL}", 
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']],
					subject: "Job: ${env.JOB_NAME}, Build: #${env.BUILD_NUMBER} - Success !",
					attachLog: true
        }
    }
}
