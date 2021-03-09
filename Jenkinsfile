#!groovy

node {

    try {
        stage 'Checkout'
            checkout scm

        stage 'Test'
            sh 'python3 -m venv venv'
            sh 'source venv/bin/activate'
            sh 'pip install -r requirements.txt'
            sh 'python manage.py test'
    }

    catch (err) {
        sh "echo 'something has gone wrong'"

        throw err
    }

}
