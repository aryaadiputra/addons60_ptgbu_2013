<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<style type="text/css">
			.break { page-break-after: always; }
		
			.center
			{
			text-align:center;
			}
			
			.italic
			{
			font-style:italic;
			}
			
			table.general
			{
			border-collapse:collapse;
			border: black solid thin;
			padding:10px;
			width:100%;
			}
			
			td.line
			{
			padding:5px;
			}
			
			td.subtiltle
			{
			border-top-left-radius: 10px 10px;
			border-bottom-left-radius: 10px 10px;
			border-top-right-radius: 10px 10px;
			border-bottom-right-radius: 10px 10px;
			font-size:18px;
			padding:10px;
			background-color:#338424;
			color:white;
			}
			
			th
			{
			border-top-right-radius: 5px 5px;
			border-top-left-radius: 5px 5px;
			padding:5px;
			color:white;
			background-color:#4bc935;
			}
			
			td.space
			{
			color:white;
			}
			
			.ttd
			{
			text-align:center;
			padding-bottom:80px;
			width:50%
			}
			
			.nama
			{
			text-align:center;
			width:50%;
			font-weight:bold;
			}
			td {font-size:11pt;}
			td.curr
				{
				text-align:right;
				}
			td.curr_total
				{
				text-align:right;
				background-color:black;
				color: white;
				font-weight:bold;
				}
			td.line
				{
				height: 400px;
				}
		</style>
	</head>
	<body>
		<% setLang('id_ID' or 'en_US') %>
		<h2 class="center">DAFTAR KARYAWAN</h2>
		%for o in objects:
			<table width=100% height="100%">	
            <tr>
            	<td class="space"></td>
            </tr>
    		<tr>
	    		<td>Department</td>
	    		<td>: ${o.department_id.name}</td>
    		</tr>
    		<tr>
	    		<td>Seksi</td>
	    		<td>: ${o.section.name}</td>
    		</tr>
    		</table>
    		<table width=100% height="100%">
			<tr>
				<th>No</th>
				<th>NIK</th>
				<th>Nama</th>
				<th>Jabatan</th>
				<th>Nomor SK</th>
				<th>Tanggal Masuk</th>
				<th>Penempatan</th>
				<th>Grade</th>
			</tr>
		
			<tr>
				<td align='center'></td>
				<td>${o.nik}</td>
				<td>${o.resource_id.name}</td>
				<td>${o.job_id.name}</td>
				<td>${o.admission_letter}</td>
				<td>${o.admission_date}</td>
				<td>${o.type}</td>
				<td>${o.current_job_level.name}</td>
			</tr>
				
				<tr>
				<td> </td>
							<td> </td>
							<td> </td>
				</tr>
			%endfor
		</table>
	</body>
</html>