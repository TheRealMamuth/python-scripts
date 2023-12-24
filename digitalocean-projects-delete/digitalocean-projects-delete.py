import argparse
import digitalocean

def delete_projects(token, keep_ids):
    manager = digitalocean.Manager(token=token)
    projects = manager.get_all_projects()

    for project in projects:
        if project.id not in keep_ids:
            print(f"Usuwanie projektu o ID: {project.id} i nazwie: {project.name}")
            project.delete()
        else:
            print(f"Zachowanie projektu o ID: {project.id} i nazwie: {project.name}")

def main():
    parser = argparse.ArgumentParser(description="Usuń projekty DigitalOcean oprócz określonych.")
    parser.add_argument("--token", required=True, help="Token API DigitalOcean")
    parser.add_argument("--keep-ids", nargs='+', required=True, help="Lista ID projektów do zachowania")

    args = parser.parse_args()
    delete_projects(args.token, args.keep_ids)

if __name__ == "__main__":
    main()
