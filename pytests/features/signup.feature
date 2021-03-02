# Created by eliasshaeffer at 3/1/21
Feature: Sign up
  Way for new allies to sign up for the service

  Scenario: I click on the signup button
    Given I go to home page
    When I click the button with id: "sign-up"
    Then I should be on page with url: "http://127.0.0.1:8000/sign-up/"

  Scenario: I have navigated to the sign-up page and I've selected undergrad as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "undergradCheck"
    Then I should see element with id: "major"

  Scenario: I have navigated to the sign-up page and I've selected grad as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "gradCheck"
    Then I should see element with id: "mentoring"

  Scenario: I have navigated to the sign-up page and I've selected faculty as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "facultyCheck"
    Then I should see element with id: "current_openings"

  Scenario: I have navigated to the sign-up page and I've selected staff as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "staffCheck"
    Then I should see element with id: "how_assist"