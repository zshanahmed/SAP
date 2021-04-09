// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

import { listify } from './StudentCategories.js';

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var undergradsPerYear = document.getElementById("numUndergradPerYear").innerText;
undergradsPerYear = listify(undergradsPerYear);

var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ["Freshman", "Sophomore", "Junior", "Senior"],
    datasets: [{
      data: undergradsPerYear,
      backgroundColor: ['#4a4dff', '#ffbc47', '#fc4c4c', '#4f4f4f'],
      hoverBackgroundColor: ['#3a3dc9', '#e0a63f', '#de3c3c', '#000000'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: true,
    },
    cutoutPercentage: 50,
  },
});
