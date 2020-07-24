#!/usr/bin/env python3

import argparse
import subprocess
import os

def check_for_salmon(path_to_salmon_bash_file = False):
	'''
	Check if salmon is installed by simply calling it or take 
	a path to a bash file in some bin and see if salmon is 
	present there. 
	'''
	try:
		if path_to_salmon_bash_file:
			output = subprocess.check_output([path_to_salmon_bash_file, "--version"])
		else:
			output = subprocess.check_output(["salmon", "--version"])	
	except (FileNotFoundError, subprocess.CalledProcessError) as error:
		print("Salmon is not present on the system. Now quitting...")
		return False
	
	#Examine the output.
	#print(output)
	if "salmon" in str(output):
		#Salmon is present. All ok.
		return True
	else:
		#Salmon is probably abesent.
		print("Salmon is not present on the system. Now quitting...")
		return False


def check_input_files(transcriptome_reference, read_files_directory):
	#See for reference.
	if os.path.exists(transcriptome_reference) and os.path.exists(read_files_directory):
		return True
	else:
		print("Reference file or the raw fastq file directory is not present.")
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
			if file.endswith("_shuffled_1.fq"):	
				fastq_file_1_path = abs_path_of_file
			elif file.endswith("_shuffled_2.fq"):
				fastq_file_2_path = abs_path_of_file

	if fastq_file_1_path is None or fastq_file_2_path is None:
		return None, None, False
	else:
		return fastq_file_1_path, fastq_file_2_path, True


def create_output_directory(output_files_directory_path):
	if os.path.exists(output_files_directory_path):
		return True
	else:
		os.mkdir(output_files_directory_path)


def run_salmon_with_bam(salmon_path, transcriptome_reference, read_files_directory, output_files_directory):
	#Assuming read files directory has BAM files, because we're using GDC/TCGA data.
	for file in os.listdir(read_files_directory):
		output_file_path = output_files_directory + '/' + file + "quant.sf"
		try:
			output = subprocess.check_output([salmon_path, "quant", "-t", transcriptome_reference, '--libType', 'A', '-a', read_files_directory + file, '-o', output_file_path])
		except subprocess.CalledProcessError:
			print("Some error while running Salmon. Please refer to terminal messages for more info.")
	return


def run_salmon_with_fastq(salmon_path, transcriptome_reference, file_1_path, file_2_path, output_files_directory):
	#Salmon creates a directory for output if fastq files are given.
	output_path = output_files_directory.rstrip('\n') + '/' + file_1_path.split('/')[-1].replace("_1.fq", "") + '/'
	#print(output_path)
	#return
	try:
		output = subprocess.check_output([salmon_path, "quant", "-i", transcriptome_reference, "-l", "A", "-1", file_1_path, "-2", file_2_path, "--validateMappings", "-o", output_path])
	except subprocess.CalledProcessError:
			print("Some error while running Salmon. Please refer to terminal messages for more info.")
	return 		


def main():
	parser = argparse.ArgumentParser()

	#Arguments.
	parser.add_argument("-r", "--transcriptome-reference", help="Path to the reference transcriptome, should be salmon indexed if using fastq files..", required=True)
	parser.add_argument("-d", "--read-files-directory", help="Path to directory in which fastqor bam files are present.", required=False)
	parser.add_argument("-o", "--output-files-directory", help="Path to output directory.", required=True)
	parser.add_argument("-s", "--salmon-path", help="Path to salmon's bash file in some bin that is not in your path variable.", required=False)
	parser.add_argument("-b", "--use-bam", help="Sending a .bam file instead of two .fastqs.", action="store_true")
	

	#Parse and gather whatever the user sent.
	args = vars(parser.parse_args())
	salmon_path = args['salmon_path']
	transcriptome_reference = args['transcriptome_reference']
	read_files_directory = args['read_files_directory']
	output_files_directory = args['output_files_directory']
	if_bam = args['use_bam']

	#Check if salmon exists on the user's system.
	check_salmon_result = check_for_salmon(salmon_path)

	#Check if reference files and fastq files' directory exists.
	check_files_result = check_input_files(transcriptome_reference, read_files_directory)

	if not check_salmon_result or not check_files_result:
		#Main going back without completing the task, because salmon is not present on the system
		#or the files are absent.
		return False
	
	create_output_directory(output_files_directory)


	#Put salmon into salmon_path variable if salmon is present and is in user's PATH variable.
	if salmon_path is None:
		salmon_path = "salmon"

	#Run Salmon.
	if if_bam:
		#BAM mode has different way of running. It processes all bam files inside a directory.
		output = run_salmon_with_bam(salmon_path, transcriptome_reference, read_files_directory, output_files_directory)
	else:
		#Fastq files mode takes a directory and picks fastq files from it.
		#Check if two fastqs exist.
		file_1_path, file_2_path, status = check_if_two_fastqs_exist(read_files_directory)
		if not status:
			print("Read files absent.")
			exit()

		#Run salmon with 2 fastq files.
		output = run_salmon_with_fastq(salmon_path, transcriptome_reference, file_1_path, file_2_path, output_files_directory)

if __name__ == "__main__":
	main()
