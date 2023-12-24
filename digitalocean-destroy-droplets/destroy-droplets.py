import argparse
import digitalocean

def main(token, memory, vcpus, regions):
    manager = digitalocean.Manager(token=token)
    droplets = manager.get_all_droplets()

    for droplet in droplets:
        mem = str(droplet.memory)
        cpu = str(droplet.vcpus)
        region = droplet.region['slug']

        if mem not in memory or cpu not in vcpus or region not in regions:
            print(f"Usuwanie dropletu o ID: {droplet.id}")
            droplet.destroy()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Usuń droplety DigitalOcean niepasujące do określonych parametrów.")
    
    parser.add_argument("--token", required=True, help="Token API DigitalOcean")
    parser.add_argument("--memory", nargs='+', required=True, help="Lista pamięci RAM dropletów do zachowania (np. '1024 2048')")
    parser.add_argument("--vcpus", nargs='+', required=True, help="Lista liczby vCPU dropletów do zachowania (np. '1 2')")
    parser.add_argument("--regions", nargs='+', required=True, help="Lista regionów dropletów do zachowania (np. 'nyc1 sfo1')")

    args = parser.parse_args()
    main(args.token, args.memory, args.vcpus, args.regions)
