<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<style>
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
		</style>
	</head>
	<body>
		%for o in get_object(data):
		<% setLang('id_ID' or 'en_US') %>
		<h2 class="center">DAFTAR RIWAYAT HIDUP</h2>
		<h2 class="italic center">Curriculum Vitae</h2>
		<h2 class="center">${helper.embed_image('jpg',o.photo, width=80, height=120)}</h2>
		<table cellpadding="5px">
			<tr>
				<td colspan="2" class="subtiltle"><b>Data Pribadi</b> / <i>Personal Detail</i></td>
			</tr>
			<tr>
				<td width=300px>Nama / <i>Name</i></td>
				<td>: ${o.name}</td>
			</tr>
			<tr>
				<td>Alamat / <i>Address</i></td>
				<td>: ${o.address_home_id.street or ""}</td>
			</tr>
			<tr>
				<td>Kode Pos / <i>Postal Code</i></td>
				<td>: ${o.address_home_id.zip or ""}</td>
			</tr>
			<tr>
				<td>Telepon / <i>Phone</i></td>
				<td>: ${o.mobile_phone or ""}</td>
			</tr>
			<tr>
				<td>Email</td>
				<td>: ${o.work_email or ""}</td>
			</tr>
			<tr>
				<td>Jenis Kelamin / <i>Gender</i></td>
				<td>: ${get_gender(o.gender) or ""}</td>
			</tr>
			<tr>
				<td>Golongan Darah / <i>Blood Type</i></td>
				<td>: ${get_gender(o.blood_type) or ""}</td>
			</tr>
			<tr>
				<td>Tanggal Lahir / <i>Date of Birth</i></td>
				<td>: ${get_date(o.birthday) or ""}</td>
			</tr>
			<tr>
				<td>Status Pernikahan / <i>Marital Status</i></td>
				<td>: ${o.marital.name or ""}</td>
			</tr>
			<tr>
				<td>Kewarganegaraan / <i>Nationality</i></td>
				<td>: ${o.country_id.name or ""}</td>
			</tr>
			<tr>
				<td>Agama / <i>Religion</i></td>
				<td>: ${o.religion_id.name or ""}</td><br />
			</tr>
			<tr><td class="space">space</td></tr>
			<tr>
				<td colspan="2" class="subtiltle"><b>Data Pekerjaan</b> / <i>Current Job Information</i></td>
			</tr>
			<tr>
				<td width=300px>Penempatan / <i>Placement</i></td>
				<td>: ${o.type}</td>
			</tr>
			<tr>
				<td>Lokasi / <i>Location</i></td>
				<td>: ${o.work_location or ""}</td>
			</tr>
			<tr>
				<td>NIK / <i>NIK</i></td>
				<td>: ${o.nik}</td>
			</tr>
			<tr>
				<td>NIK BOB / <i>NIK BOB</i></td>
				<td>: ${o.nik_bob or "-"}</td>
			</tr>
			<tr>
				<td>Departemen / <i>Department</i></td>
				<td>: ${o.department_id.name}</td>
			</tr>
			<tr>
				<td>Seksi / <i>Section</td>
				<td>: ${o.section.name or "-"}</td>
			</tr>
			<tr>
				<td>Jabatan / <i>Job Position</i></td>
				<td>: ${o.job_id.name}</td>
			</tr>
			<tr>
				<td>Nomor SK/ <i>Admission No.</i></td>
				<td>: ${o.admission_letter}</td>
			</tr>
			<tr>
				<td>Tanggal Masuk/ <i>Admission Date</i></td>
				<td>: ${get_date(o.admission_date)}</td>
			</tr>
			<tr><td class="space">space</td></tr>
			<tr>
				<td colspan="2" class="subtiltle"><b>Riwayat Pendidikan</b> / <i>Educational History</i></td>
			</tr>
			<tr>
				<td colspan="2">
					<table width="100%">
						<tr>
							<th width="80px"><b>Mulai</b> / <i>Start</i></td>
							<th width="80px"><b>Selesai</b> / <i>End</i></td>
							<th width="80px"><b>Strata</b> / <i>Grade</i></td>
							<th><b>Jurusan</b> / <i>Major</i></td>
							<th><b>Nama Sekolah</b> / <i>Institution</i></td>
						</tr>
						<%c=0%>
						%for e in o.education_id:
							%if c%2==0:
								<tr bgcolor="#d0ec93">
							%else:
								<tr>
							%endif
									<td class="center line">${e.edu_from or "-"}</td>
									<td class="center line">${e.edu_to or "-"}</td>
									<td class="line">${e.degree or "-"}</td>
									<td class="line">${e.subject or "-"}</td>
									<td class="line">${e.name or "-"}</td>
								</tr>
							<%c+=1%>
						%endfor
					</table>
				</td>
			</tr>
			<tr><td class="space">space</td></tr>
			<tr>
				<td colspan="2" class="subtiltle"><b>Riwayat Pelatihan</b> / <i>Training History</i></td>
			</tr>
			<tr>
				<td colspan="2">
					<table width="100%">
						<tr>
							<th width="80px">Mulai</th>
							<th width="80px">Selesai</th>
							
							<th width="80px">Nama Training</th>
						</tr>
						<%c=0%>
						%for e in o.training_line:
							%if c%2==0:
								<tr bgcolor="#d0ec93">
							%else:
								<tr>
							%endif
									<td class="center line">${get_date(e.date_start) or "-"}</td>
									<td class="center line">${get_date(e.date_end) or "-"}</td>
									<td class="line">${e.name or "-"}</td>
								</tr>
							<%c+=1%>
						%endfor
					</table>
				</td>
			</tr>
			<tr><td class="space">space</td></tr>
			<tr>
				<td colspan="2" class="subtiltle"><b>Pengalaman Kerja</b> / <i>Job Experiences</i></td>
			</tr>
			<tr>
				<td colspan="2">
					<table width="100%">
						<tr>
							<th width="80px"><b>Dari</b> / <i>From</i></th>
							<th width="80px"><b>Sampai</b> / <i>To</i></th>
							<th><b>Perusahaan</b> / <i>Company</i></th>
							<th><b>Jabatan Terakhir</b> / <i>Last Job</i></th>
						</tr>
						<%c=0%>
						%for exp in o.experience_id:
							%if c%2==0:
								<tr bgcolor="#d0ec93">
							%else:
								<tr>
							%endif
									<td class="line">${exp.exp_from or "-"}</td>
									<td class="line">${exp.exp_to or "-"}</td>
									<td class="line">${exp.name or "-"}</td>
									<td class="line">${exp.exp_position or "-"}</td>
								</tr>
							<%c+=1%>
						%endfor
					</table>
				</td>
			</tr>
			<tr><td class="space">space</td></tr>
			<tr>
				<td colspan="2" class="subtiltle"><b>Daftar Keluarga</b> / <i>Family</i></td>
			</tr>
			<tr>
				<td><b>Tanggal Menikah</b> / <i>Marriage Date</i></td>
				<td>: </td>
			</tr>
			<tr>
				<td colspan="2">
					<table width="100%">
						<tr>
							<th><b>Name</b> / <i>Name</i></th>
							<th><b>Relasi</b> / <i>Relation</i></th>
							<th><b>Tempat,Tanggal Lahir</b> / <i>Birth Place,Date</i></th>
						</tr>
						<%c=0%>
						%for fam in o.family_id:
							%if c%2==0:
								<tr bgcolor="#d0ec93">
							%else:
								<tr>
							%endif
									<td class="line">${fam.name or "-"}</td>
									<td class="line">${fam.relation.name or "-"}</td>
									<td class="line">${fam.place_of_birth}, ${get_date(fam.birthday)}</td>
								</tr>
							<%c+=1%>
						%endfor
					</table>
				</td>
			</tr>
		</table>
		%endfor
	</body>
</html>