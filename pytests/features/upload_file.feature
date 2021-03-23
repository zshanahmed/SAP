# Created by eliasshaeffer at 3/22/21
Feature: Upload Feature
IBA admin should have the ability to upload files and create allies in the previous data or our downloaded CSV format.

  Scenario: I click the button to download a csv
    Given I am on dashboard logged in as admin
    When I click the button with id: "uploadCsv"
    Then I should see a file viewer

  Scenario: I upload some allies
    Given I am on dashboard logged in as admin
    When I click the button with id: "uploadCsv"
    And I select file with name: "allies.csv"
    And I click the button with id: "submit"
    Then I should see entries with names: "elias, zeeshan, nam, bigGoonga"