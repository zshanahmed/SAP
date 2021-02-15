# Created by eliasshaeffer at 2/14/21
Feature: initial testing
  As a developer
  so that I can test pytest-bdd
  I would like to see if I can write an acceptance test in pytest-bdd

  Scenario: Check Title of initial template
    When I'm on the homepage
    Then I should see: "Polls app"