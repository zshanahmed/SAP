Feature: Login

  As an IBA admin
  So that I can access data of members and manage events
  I want to login with my username and password

  Scenario: I want to login
    Given that I am on the login page
    When I enter my username johndoe and password serpent_1
    Then I should see the page with title Dashboard