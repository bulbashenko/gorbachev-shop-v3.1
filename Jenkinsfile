pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'your-credentials-id', url: 'https://github.com/bulbashenko/gorbachev-shop-v3.1.git'
            }
        }
        stage('Frontend Build & Test') {
            steps {
                dir('frontend') {
                    bat 'npm install'
                    bat 'npm run build'
                    bat 'npm test'
                }
            }
        }
        stage('Backend Build & Test') {
            steps {
                dir('backend') {
                    bat 'pip install -r requirements.txt'
                    bat 'python manage.py test'
                }
            }
        }
    }
}
