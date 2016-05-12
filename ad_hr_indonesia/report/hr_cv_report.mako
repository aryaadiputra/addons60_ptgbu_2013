<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<%
		import addons
		path=addons.get_module_resource("ad_hr_indonesia/static/jquery-1.8.3.min.js")
		%>
		<script src="${path}" type="text/javascript"></script>
		<style>
			table{
			}
			.italic {
				font-style:italic;
				}
			h2{
			font-size:16pt;
			}
			tr
				{
				page-break-inside:avoid; 
				page-break-before:always;
				}
			th
				{
				font-size:14pt;
				font-weight:bold;
				}
			td
				{
				font-size:11pt;
				word-break:normal;
				padding:3px;
				}
			.satu {
				width:250px;
			}
			tiga {
				width:400px;
			}
			.breakdata{
				padding-left:30px;
				padding-right:20px;
				vertical-align:text-top;
				}
			.label
				{
				padding-left:30px;
				padding-right:10px;
				vertical-align:text-top;
				}
			.data
				{
				padding-left:10px;
				padding-right:20px;
				vertical-align:text-top;
				}
			.separator
				{
				text-align:center;
				vertical-align:text-top;
				}
			.subheading
				{
				page-break-before:auto;
				border-top-left-radius: 10px 10px;
				border-bottom-left-radius: 10px 10px;
				border-top-right-radius: 10px 10px;
				border-bottom-right-radius: 10px 10px;
				padding-top:5px;
				padding-bottom:5px;
				padding-left:20px;
				background-color:#338424;
				color:white;
				text-align:left;
				}
			.breakdataheading
				{
				font-size:12pt;
				font-weight:bold;
				vertical-align:text-top;
				}
			.breakdatarows
				{
				font-size:12pt;
				vertical-align:text-top;
				}
		</style>
		<script>
			var ntable=${len(objects)}	
			$(document).ready(function(){
				$('table:last-child').css('page-break-after',"auto");
				$('center:first-child').css('page-break-before',"auto");
			})
		</script>
	</head>
<body>
	<% 
	ntable=0 
	%>
	%for o in objects:
		<% setLang('id_ID' or 'en_US') %>
		<center style="page-break-before:always;">
			<h2>DAFTAR RIWAYAT HIDUP</h2>
			<h2 class="italic">Curriculum Vitae</h2>
			<h2 class="center">${helper.embed_image('jpg',o.photo, width=113.385826772, height=151.181102362)}</h2>
		</center>
		<table width="100%" style="page-break-before:auto;">
			<tr>
				<td width="100%">
					<table width="100%" style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>Data Pribadi</b> / <i>Personal Detail</i></th>
						</tr>
						<tr>
							<td class="satu label">Nama / <i>Name</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.name}</td>
						</tr>
						<tr>
							<td class="satu label">Alamat / <i>Address</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.address_home_id.street or ""}</td>
						</tr>
						<tr>
							<td class="satu label">Kode Pos / <i>Postal Code</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.address_home_id.zip or ""}</td>
						</tr>
						<tr>
							<td class="satu label">Telepon / <i>Phone</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.mobile_phone or ""}</td>
						</tr>
						<tr>
							<td class="satu label">Email</td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.work_email or ""}</td>
						</tr>
						<tr>
							<td class="satu label">Jenis Kelamin / <i>Gender</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${get_gender(o.gender) or ""}</td>
						</tr>
						<tr>
							<td class="satu label">Golongan Darah / <i>Blood Type</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${get_blood(o.blood_type) or ""}</td>
						</tr>
						<tr>
							<td class="satu label">Tanggal Lahir / <i>Date of Birth</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${get_date(o.birthday) or ""}</td>
						</tr>
						<tr>
							<td class="satu label">Status Pernikahan / <i>Marital Status</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.marital.name or "-"}</td>
						</tr>
						<tr>
							<td class="satu label">Kewarganegaraan / <i>Nationality</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.country_id.name or "-"}</td>
						</tr>
						<tr>
							<td class="satu label">Agama / <i>Religion</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.religion_id.name or ""}</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr>
				<td width="100%">
					<table width="100%" style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>Data Pekerjaan</b> / <i>Current Job Information</i></th>
						</tr>
						<tr>
							<td class="satu label">Penempatan / <i>Placement</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">
								%if o.type == bsp:
									Head Office
								%elif o.type == bob:
									OnSite
								%endif
							</td>
						</tr>
						<tr>
							<td class="satu label">Lokasi / <i>Location</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.work_location.title() or ""}</td>
						</tr>
						<tr>
							<td class="satu label">NIK / <i>NIK</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.nik}</td>
						</tr>
						<tr>
							<td class="satu label">Grade</td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.current_job_level.name or "-"}</td>
						</tr>
						<tr>
							<td class="satu label">NIK OnSite / <i>NIK OnSite</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.nik_bob or "-"}</td>
						</tr>
						<tr>
							<td class="satu label">Departemen / <i>Department</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.department_id.name}</td>
						</tr>
						<tr>
							<td class="satu label">Seksi / <i>Section</td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.section.name or "-"}</td>
						</tr>
						<tr>
							<td class="satu label">Jabatan / <i>Job Position</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${o.job_id.name}</td>
						</tr>
						<tr>
							<td class="satu label">Tanggal Masuk/ <i>Admission Date</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${get_date(o.admission_date)}</td>
						</tr>
						<tr><td class="space" colspan="3">&nbsp;</td></tr>
					</table>
				</td>
			</tr>
			<tr>
				<td width="100%">
					<table width="100%" summary="RIWAYAT PENDIDIKAN"  style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>Riwayat Pendidikan</b> / <i>Educational History</i></th>
						</tr>
						<tr>
							<td colspan="3" class="breakdata">
								<table width="100%">
									<tr>
										<td class="breakdataheading" width="80px"><b>Mulai</b> / <i>Start</i></td>
										<td class="breakdataheading" width="80px"><b>Selesai</b> / <i>End</i></td>
										<td class="breakdataheading" width="80px"><b>Strata</b> / <i>Grade</i></td>
										<td class="breakdataheading"><b>Jurusan</b> / <i>Major</i></td>
										<td class="breakdataheading"><b>Nama Sekolah</b> / <i>Institution</i></td>
									</tr>
									<%c=0%>
									%for e in o.education_id:
										%if c%2==0:
											<tr bgcolor="#d0ec93">
										%else:
											<tr>
										%endif
												<td class="breakdatarows center line">${e.edu_from or "-"}</td>
												<td class="breakdatarows center line">${e.edu_to or "-"}</td>
												<td class="breakdatarows line">${e.degree or "-"}</td>
												<td class="breakdatarows line">${e.subject or "-"}</td>
												<td class="breakdatarows line">${e.name or "-"}</td>
											</tr>
										<%c+=1%>
									%endfor
								</table>
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr><td class="space" colspan="3">&nbsp;</td></tr>
			<tr>
				<td width="100%">
					<table width="100%" summary="RIWAYAT PELATIHAN" style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>Riwayat Pelatihan</b> / <i>Training History</i></th>
						</tr>
						<tr>
							<td colspan="3" class="breakdata">
								<table width="100%">
									%if o.training_line:
										<tr>
											<td class="breakdataheading" width="80px">Mulai</td>
											<td class="breakdataheading" width="80px">Selesai</td>
											
											<td class="breakdataheading" width="80px">Nama Training</td>
										</tr>
										<%c=0%>
										%for e in o.training_line:
											%if c%2==0:
												<tr bgcolor="#d0ec93">
											%else:
												<tr>
											%endif
													<td class="breakdatarows center line">${get_date(e.date_start) or "-"}</td>
													<td class="breakdatarows center line">${get_date(e.date_end) or "-"}</td>
													<td class="breakdatarows line">${e.name or "-"}</td>
												</tr>
											<%c+=1%>
										%endfor
									%else:
										<tr>
											<td class="breakdataheading" width="80px"><center>Mulai</center></td>
											<td class="breakdataheading" width="80px"><center>Selesai</center></td>
											
											<td class="breakdataheading" width="80px"><center>Nama Training</center></td>
										</tr>
										<tr>
											<td class="breakdatarows center line"><center>-</center></td>
											<td class="breakdatarows center line"><center>-</center></td>
											<td class="breakdatarows line"><center>-</center></td>
										</tr>
									%endif
								</table>
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr><td class="space" colspan="3">&nbsp;</td></tr>
			<tr>
				<td width="100%">
					<table width="100%" summary="RIWAYAT PENGALAMAN" style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>Pengalaman Kerja</b> / <i>Job Experiences</i></th>
						</tr>
						<tr>
							<td colspan="3" class="breakdata">
								<table width="100%">
									<tr>
										<td class="breakdataheading" width="80px"><b>Dari</b> / <i>From</i></td>
										<td class="breakdataheading" width="80px"><b>Sampai</b> / <i>To</i></td>
										<td class="breakdataheading"><b>Perusahaan</b> / <i>Company</i></td>
										<td class="breakdataheading"><b>Jabatan Terakhir</b> / <i>Last Job</i></td>
									</tr>
									<%c=0%>
									%for exp in o.experience_id:
										%if c%2==0:
											<tr bgcolor="#d0ec93">
										%else:
											<tr>
										%endif
												<td class="breakdatarows line">${exp.exp_from or "-"}</td>
												<td class="breakdatarows line">${exp.exp_to or "-"}</td>
												<td class="breakdatarows line">${exp.name or "-"}</td>
												<td class="breakdatarows line">${exp.exp_position or "-"}</td>
											</tr>
										<%c+=1%>
										
									%endfor
								</table>
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr><td class="space" colspan="3">&nbsp;</td></tr>
			<tr>
				<td width="100%">
					<table width="100%" summary="RIWAYAT PELATIHAN" style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>Daftar Keluarga</b> / <i>Family</i></th>
						</tr>
						<tr>
							<td class="satu label"><b>Tanggal Menikah</b> / <i>Marriage Date</i></td>
							<td class="dua separator">:</td>
							<td class="tiga data">${get_date(o.marriage_date)}</td>
						</tr>
						<tr>
							<td colspan="3" class="breakdata">
								<table width="100%">
									<tr>
										<td class="breakdataheading"><b>Name</b> / <i>Name</i></td>
										<td class="breakdataheading"><b>Relasi</b> / <i>Relation</i></td>
										<td class="breakdataheading"><b>Tempat,Tanggal Lahir</b> / <i>Birth Place,Date</i></td>
									</tr>
									<%d=0%>
									%for fam in o.family_id:
										%if d%2==0:
											<tr bgcolor="#d0ec93">
										%else:
											<tr>
										%endif
												<td class="breakdatarows line">${fam.name or "-"}</td>
												<td class="breakdatarows line">${fam.relation.name or "-"}</td>
												<td class="breakdatarows line">${fam and fam.place_of_birth or "-"},${fam and get_date(fam.birthday) or "-"}</td>
											</tr>
										<% d+=1 %>
									%endfor
								</table>
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr>
				<td width="100%">
					<table width="100%" summary="RIWAYAT MUTASI" style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>Riwayat Mutasi</b> / <i>Mutation History</i></th>
						</tr>
						
					</table>
				</td>
			</tr>
			<tr>
				<td width="100%">
					<table width="100%" summary="PMS" style="page-break-before:auto;">
						<tr>
							<th colspan="3" class="subheading"><b>PMS</b> / <i>PMS Record</i></th>
						</tr>
						<tr>
							<td colspan="3" class="breakdata">
								<table width="100%">
									%if o.rate:
										<tr>
											<td class="breakdataheading" width="80px">Tahun</td>
											<td class="breakdataheading" width="80px">Rate</td>
											<td class="breakdataheading">Catatan</td>
										</tr>
										<%c=0%>
										%for e in o.rate:
											%if c%2==0:
												<tr bgcolor="#d0ec93">
											%else:
												<tr>
											%endif
													<td class="breakdatarows center line">${e.year or "-"}</td>
													<td class="breakdatarows center line">${e.rate or "-"}</td>
													<td class="breakdatarows line">${e.notes or "-"}</td>
												</tr>
											<%c+=1%>
										%endfor
									%else:
										<tr>
											<td class="breakdataheading" width="80px"><center>Tahun</center></td>
											<td class="breakdataheading" width="80px"><center>Rate</center></td>
											<td class="breakdataheading" width="80px"><center>Catatan</center></td>
										</tr>
										<tr>
											<td class="breakdatarows center line"><center>-</center></td>
											<td class="breakdatarows center line"><center>-</center></td>
											<td class="breakdatarows line"><center>-</center></td>
										</tr>
									%endif
								</table>
							</td>
						</tr>
					</table>
				</td>
			</tr>
		<%ntable+=1%>
		</table>
	%endfor
</body>
</html>
