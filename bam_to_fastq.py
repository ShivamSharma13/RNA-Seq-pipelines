#!/usr/bin/env python3

import argparse
import subprocess
import os


'''
This script taken in an input directory and converts all the bam files inside it to two fastq files.

Accepts: an Input Directory, and an Output Directory.

'''
def get_paths_of_bam_files(input_directory):
	paths_of_bam_files = []
	if not os.path.exists(input_directory):
		return False
	for root, dirs, files in os.walk(input_directory, topdown=True):
		for file in files:
			if file.endswith(".bam"):
				relative_path_of_file = os.path.join(root, file)
				abs_path_of_file = os.path.abspath(relative_path_of_file)
				paths_of_bam_files.append(abs_path_of_file)

	return paths_of_bam_files


def convert_bam_to_fastq(paths_of_bam_files):
	#Check for tools.
	try:
		bash = subprocess.check_output(["bedtools", "--version"])
		#bash = subprocess.check_output(["samtools", "--version"])
	except (FileNotFoundError, subprocess.CalledProcessError) as e:
		print("Some tools are missing. \n{}".format(e))
		return False

	#Shuffle BAM files to remove bias.
	for bam_file in paths_of_bam_files[:20]:
		#Maintain a log-like file.
		with open("bam_files_completed.txt", 'a') as f:
			f.write(bam_file)

		#Creating paths to send to tools.
		shuffled_file_path = bam_file.replace("sorted", "shuffled")
		tmp_dir_path = "/".join(bam_file.split("/")[:-1]) + '/' + "tmp"

		read_one_name = "/".join(bam_file.split("/")[:-1]) + '/' + bam_file.split("/")[-1] + "_1.fq"
		read_two_name = "/".join(bam_file.split("/")[:-1]) + '/' + bam_file.split("/")[-1] + "_2.fq"

		#Running tools.
		try:
			print("Shuffling BAM file: {} using samtools collate.".format(bam_file))
			bam_to_fastq = subprocess.check_output(["samtools", "collate", "-o", shuffled_file_path, bam_file, "--threads", "4"])

			#Initiate bedtools for bam to fastq.
			print("Converting bam to fastq file: {} using bedtools.".format(bam_file))
			bam_to_fastq = subprocess.check_output(["samtools", "bam2fq", "-1", read_one_name, "-2", read_two_name, shuffled_file_path, "--threads", "4"])
		
			#Remove the qsort file.
			print("Removing the sorted BAM file.")
			remove_file = subprocess.check_output(["rm", shuffled_file_path])
		except subprocess.CalledProcessError:
			print("Couldn't complete conversion.\n {}".format(subprocess.CalledProcessError.output))
		print("Conversion completed for\n========>{}".format(bam_file))


	return True

def	bam_to_fastq_wrapper():
	parser = argparse.ArgumentParser()

	#Arguments.
	parser.add_argument("-i", "--input-directory", help="Path to the Input Directory.", required=False)
	parser.add_argument("-f", "--shortcut_file", help="Path to a file which has paths to bam files.", required=False)

	#Parse and gather whatever the user sent.
	args = vars(parser.parse_args())
	input_directory = args['input_directory']
	shortcut_file = args['shortcut_file']

	if shortcut_file:
		print("Shortcut file provided...\nReading file: {}".format(shortcut_file))
		with open(shortcut_file) as f:
			raw = f.read()
		bam_files_path = raw.split('\n')

	else:
		bam_files_path = get_paths_of_bam_files(input_directory)
		print("BAM files found:\n{}".format(bam_files_path))
	
		with open("bam_files_info.txt", 'w') as f:
			f.write("\n".join(bam_files_path))
	
	process_status = convert_bam_to_fastq(bam_files_path)

	if process_status is False:
		print("Process failed!")
	else: 
		print("Process completed, quitting!")

if __name__ == "__main__":
	bam_to_fastq_wrapper()
