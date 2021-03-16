# Created by eliasshaeffer at 3/15/21
Feature: Download csv
Should be able to download all the data in csv format from the dashboard


  Background: I am on dashboard logged in as admin
    Given I am on dashboard logged in as admin

  Scenario: I click the download csv button to download the data.
    When I click the button with id: "downloadCsv"
    Then I should have the csv file in my downloads