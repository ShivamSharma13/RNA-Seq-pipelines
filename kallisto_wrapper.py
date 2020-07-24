#!/usr/bin/env python3

import argparse
import subprocess
import os

def check_for_kallisto(path_to_kallisto_bash_file = False):
	'''
	Check if kallisto is installed by simply calling it or take 
	a path to a bash file in some bin and see if kallisto is 
	present there. 
	'''
	try:
		if path_to_kallisto_bash_file:
			output = subprocess.check_output([path_to_kallisto_bash_file, "--version"])
		else:
			output = subprocess.check_output(["kallisto", "version"])	
	except (FileNotFoundError, subprocess.CalledProcessError) as error:
		print("Kallisto is not present on the system. Now quitting... {}".format(error))
		return False
	
	#Examine the output.
	#print(output)
	if "kallisto" in str(output):
		#Kallisto is present. All ok.
		return True
	else:
		#Kallisto is probably abesent.
		print("Kallisto is not present on the system. Now quitting...")
		return False


def check_if_two_fastqs_exist(read_files_directory):
	'''
	See if two fastq files exists, if they do, send their paths, otherwise return False.
	returns path_1, path_2, True
	'''
	fastq_file_1_path = None
	fastq_file_2_path = None
	for root, dirs, files in os.walk(read_files_directory, topdown=True):
		for file in files:
			relative_path_of_file = os.path.join(root, file)
			abs_path_of_file = os.path.abspath(relative_path_of_file)
			if file.endswith("_1.fq"):	
				fastq_file_1_path = abs_path_of_file
			elif file.endswith("_2.fq"):
				fastq_file_2_path = abs_path_of_file

	if fastq_file_1_path is None or fastq_file_2_path is None:
		return None, None, False
	else:
		return fastq_file_1_path, fastq_file_2_path, True


def create_output_directory(output_files_directory_path):
	if os.path.exists(output_files_directory_path):
		return True
	else:
		print("Creating a directory at {}".format(output_files_directory_path))
		os.mkdir(output_files_directory_path)


def run_kallisto_with_fastq(kallisto_path, transcriptome_reference, file_1_path, file_2_path, output_files_directory, input_directory):
	#Kallisto creates a directory for output if fastq files are given.
	output_path = output_files_directory.rstrip('/') + '/' + input_directory.split("/")[:-1] + "/" + "output"
	#print(output_path)
	#return
	try:
		output = subprocess.check_output([kallisto_path, "quant", "-i", transcriptome_reference, "-o", output_path, "-b", "100", file_1_path, file_2_path])
	except subprocess.CalledProcessError:
		print("Some error while running Kallisto. Please refer to terminal messages for more info.")
	return 		


def main():
	parser = argparse.ArgumentParser()

	#Arguments.
	parser.add_argument("-r", "--transcriptome-reference", help="Path to the indexed reference transcriptome file, (.idx)", required=True)
	parser.add_argument("-d", "--read-files-directory", help="Path to directory in which fastq or bam files are present.", required=False)
	parser.add_argument("-o", "--output-files-directory", help="Path to output directory.", required=True)
	parser.add_argument("-k", "--kallisto-path", help="Path to kallisto's bash file in some bin that is not in your path variable.", required=False)
	parser.add_argument("-b", "--use-bam", help="Sending a .bam file instead of two .fastqs.", action="store_true")
	
	#If you get a path to a directory where the files exists, use that.
	parser.add_argument("-f", "--file-read-files-directory", help="Text file which containes paths of directories that contain the fastq/BAM files.", required=False)	

	#Parse and gather whatever the user sent.
	args = vars(parser.parse_args())
	kallisto_path = args['kallisto_path']
	transcriptome_reference = args['transcriptome_reference']
	read_files_directory = args['read_files_directory']
	output_files_directory = args['output_files_directory']
	if_bam = args['use_bam']
	info_file = args['file_read_files_directory']

	#Check if kallisto exists on the user's system.
	check_kallisto_result = check_for_kallisto(kallisto_path)
	if not check_kallisto_result:
		#Main going back without completing the task, because kallisto is not present on the system.
		return False

	#Check if reference files exists.
	if not os.path.exists(transcriptome_reference):
		print("Reference file path is incorrect.")


	if info_file:
		############################################################################################
		#An info file has been passed. We're expecting a bunch of fastq files.
		with open(info_file) as f:
			raw = f.read()

		#Getting the file paths.
		directories = [directory for directory in raw.split('\n')]

		for directory in directories:
			#Fastq files mode takes a directory and picks fastq files from it.
			#Check if two fastqs exist.
			file_1_path, file_2_path, status = check_if_two_fastqs_exist(directory)
			if not status:
				print("Read files in directory: {} wasn't found. Skipping...".format(directory))
				continue
				
			create_output_directory(output_files_directory.rstrip("/") + "/" + directory.split("/")[-1].rstrip("/") + "/" + "output")
			print("Running Kallisto for directory: {}".format(directory))

			continue
			#Run kallisto with 2 fastq files.
			output = run_kallisto_with_fastq(kallisto_path, transcriptome_reference, file_1_path, file_2_path, output_files_director, directoryy)

	else:
		############################################################################################
		###########################Kallisto invoked on an individual file###########################
		create_output_directory(output_files_directory)

		#Put kallisto into kallisto_path variable if kallisto is present and is in user's PATH variable.
		if kallisto_path is None:
			kallisto_path = "kallisto"

		#Run Kallisto.
		if if_bam:
			#BAM mode has different way of running. It processes all bam files inside a directory.
			output = run_kallisto_with_bam(kallisto_path, transcriptome_reference, read_files_directory, output_files_directory)
		else:
			#Fastq files mode takes a directory and picks fastq files from it.
			#Check if two fastqs exist.
			file_1_path, file_2_path, status = check_if_two_fastqs_exist(read_files_directory)
			if not status:
				print("Read files absent.")
				exit()

			#Run kallisto with 2 fastq files.
			output = run_kallisto_with_fastq(kallisto_path, transcriptome_reference, file_1_path, file_2_path, output_files_directory)

if __name__ == "__main__":
	main()
