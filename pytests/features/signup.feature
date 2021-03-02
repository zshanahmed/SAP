# Created by eliasshaeffer at 3/1/21
Feature: Sign up
  Way for new allies to sign up for the service

  Scenario: I click on the signup button
    Given I go to home page
    When I click the button with id: "sign-up"
    Then I should be on page with url: "http://127.0.0.1:8000/sign-up/"