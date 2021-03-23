# Created by eliasshaeffer at 3/22/21
Feature: Upload Feature
IBA admin should have the ability to upload files and create allies in the previous data or our downloaded CSV format.

  Scenario: I click the button to upload a csv of records, but I have not selected a file
    Given I am on dashboard logged in as admin
    When I click the button with id: "submitUpload"
    Then I should see text: "Please select a file to upload!"

  Scenario: I upload some allies
    Given I am on dashboard logged in as admin
    When I select file using "uploadCsv" with name: "./pytests/assets/allies.csv"
    And I click the button with id: "submitUpload"
    Then I should see entries with names: "Elias, Zeeshan, Nam, Biggoonga"
    And I should have the error file in my downloads