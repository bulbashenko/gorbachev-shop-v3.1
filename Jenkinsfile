pipeline {
    agent any
    stages {
        stage('Frontend Build & Test') {
            steps {
                dir('frontend') {
                    sh 'npm install'
                    sh 'npm run build'
                    sh 'npm test'
                }
            }
        }
        stage('Backend Build & Test') {
            steps {
                dir('backend') {
                    sh 'pip install -r requirements.txt'
                    sh 'python manage.py test'
                }
            }
        }
    }
}
