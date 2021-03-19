# Created by eliasshaeffer at 3/15/21
Feature: Download csv
Should be able to download all the data in csv format from the dashboard

  Background: I created a non-admin account
    Given I have navigated to sign-up page
    When I fill in "haw2" into element: "new_username"
    And I fill in "name" into element: "firstName"
    And I fill in "haw2@uiowa.edu" into element: "new_email"
    And I fill in "lastName" into element: "lastName"
    And I fill in "iba_sep_1" into element: "new_password"
    And I fill in "iba_sep_1" into element: "repeat_password"
    And I click the radio button with id: "staffCheck"
    And I fill in staff form

  Scenario: I click the download csv button to download the data.
    Given I am on dashboard logged in as admin
    When I click the button with id: "downloadCsv"
    Then I should have the csv file in my downloads

  Scenario: I try to download allies when not logged in as admin
    Given I have logged in with username "haw2" and password "iba_sep_1"
    Then I should not be able to download users.
