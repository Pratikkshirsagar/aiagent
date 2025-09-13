from functions.get_files_info import get_files_info


def main():
    root_contents = get_files_info("calculator", ".")
    print(root_contents)
    pkg_content = get_files_info("calculator", "pkg")
    print(pkg_content)

    error_content = get_files_info("calculator", "/bin")
    print(error_content)

    error_content = get_files_info("calculator", "../")
    print(error_content)


main()
