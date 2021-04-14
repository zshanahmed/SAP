# Created by zeeshanahmed at 4/12/21
Feature: # Enter feature name here
  # Enter feature description here
  As an IBA admin
  So that I can delete event
  I want to goto Calendar page

  Background:
    Given I am on dashboard logged in as admin
    And I am on calendar page

  Scenario: # Enter scenario name here
    # Enter steps here
    Given I am on calendar logged in as admin
    Then I should be able to delete event with