// admin_charts.js

document.addEventListener("DOMContentLoaded", () => {
    // Bookings per Day
    const bookingLabels = JSON.parse(document.getElementById("bookingChart").dataset.labels);
    const bookingData = JSON.parse(document.getElementById("bookingChart").dataset.data);
  
    new Chart(document.getElementById('bookingChart'), {
      type: 'bar',
      data: {
        labels: bookingLabels,
        datasets: [{
          label: 'Bookings',
          data: bookingData,
          backgroundColor: '#4e73df'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: 'Bookings Per Day' }
        }
      }
    });
  
    // Occupancy per Lot
    const occLabels = JSON.parse(document.getElementById("occupancyChart").dataset.labels);
    const availableData = JSON.parse(document.getElementById("occupancyChart").dataset.available);
    const occupiedData = JSON.parse(document.getElementById("occupancyChart").dataset.occupied);
  
    new Chart(document.getElementById('occupancyChart'), {
      type: 'bar',
      data: {
        labels: occLabels,
        datasets: [
          {
            label: 'Available',
            data: availableData,
            backgroundColor: '#1cc88a'
          },
          {
            label: 'Occupied',
            data: occupiedData,
            backgroundColor: '#e74a3b'
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: 'Occupancy per Parking Lot' }
        }
      }
    });
  });
  