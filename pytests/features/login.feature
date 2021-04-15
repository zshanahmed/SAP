Feature: Login

  As an IBA admin
  So that I can access data of members and manage events
  I want to login with my username and password

  Scenario: I want to login using valid username and password
    Given that I am on the login page
    When I enter my username iba_admin and password iba_sep_1
    Then I should see the page with title Science Alliance Portal

  Scenario: I want to login using valid username and password as ally
    Given that I am on the login page
    When I enter my username john and password doe
    Then I should see the page with title Science Alliance Portal

  Scenario: I try to login with invalid username and password
    Given that I am on the login page
    When I enter my username johndoe and password johndoe
    Then I should see a message saying 'Please enter a correct username and password. Note that both fields may be case-sensitive.'

  Scenario: I forgot my password while trying to login
    Given that I am on the login page
    When I click on Forgot Password?
    Then I should see the page with title Forgot Your Password?

#  Scenario: I want to login using valid username and password as ally
#    Given that I am on the login page
#    When I enter my username john and password doe
#    Then I should see the page with title Science Alliance Portal