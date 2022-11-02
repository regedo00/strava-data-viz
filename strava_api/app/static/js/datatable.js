$(document).ready(function () {
  var table = $('#activity-table').DataTable({
    ajax: '/show-table',
    serverSide: true,
    dom: "Bftrip",
    lengthChange: false,
    buttons: ['colvis'],
    columns: [
      { data: 'id' },
      { data: 'name', searchable: true },
      { data: 'distance', orderable: true, searchable: false },
      { data: 'type', orderable: false, searchable: true },
      { data: 'start_date', orderable: true, searchable: false },
      { data: 'average_speed', orderable: true }
    ],
  });
  table.buttons().container()
    .appendTo($('div.column.is-half', table.table().container()).eq(0));
});
