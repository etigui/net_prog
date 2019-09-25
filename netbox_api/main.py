import pynetbox
import re
# Network creation order
# 1. Tenant Groups
# 2. Add Tenants
# 3. Add regions
# 4. Add Sites
# 5. Add Rack Groups
# 6. Add Rack Roles
# 7. Add Racks
# 8. Add Device Roles
# 9. Add Devices
# 10. IP ?...

STATUS_ACTIVE = 1

CISCO_SWITCH_MODEL = "IOSL21524"
CISCO_ROUTER_MODEL = "7200"

RACK_HEIGHT = 10
RACK_POS = 1

class Netbox():
    def __init__(self):
        self.__nb = pynetbox.api(
            'http://192.168.56.10:8000',
            private_key_file='key/pk.key',
            token='8ff35cbc1d7e1c4ef6d42e222b913c9f57bf7ed9'
        )

    def create_network(self, locations, tenancy):
        try:

            # Get device role and manufacturer for our device
            cisco_manufacturer_info = self.__nb.dcim.manufacturers.get(slug="cisco")
            switch_device_role_info = self.__nb.dcim.device_roles.get(slug="access-switch")
            router_device_role_info = self.__nb.dcim.device_roles.get(slug="router")

            # Create device type (manufacturer, slug, model)
            device_type_cisco_switch_info = self.__nb.dcim.device_types.create(model=CISCO_SWITCH_MODEL, slug=self.slugify(CISCO_SWITCH_MODEL), manufacturer=cisco_manufacturer_info.id)
            device_type_cisco_router_info = self.__nb.dcim.device_types.create(model=CISCO_ROUTER_MODEL, slug=self.slugify(CISCO_ROUTER_MODEL), manufacturer=cisco_manufacturer_info.id)

            # Create tenants group
            tenant_groups_name = tenancy.get("tg")
            tenant_groups_params = dict(name=tenant_groups_name, slug=self.slugify(tenant_groups_name))
            tenant_groups_info = self.__nb.tenancy.tenant_groups.create(tenant_groups_params)

            # Create tenant
            tenant_name = tenancy.get("t")
            tenants_params = dict(name=tenant_name, slug=self.slugify(tenant_name), group=tenant_groups_info.id)
            tenants_info = self.__nb.tenancy.tenants.create(tenants_params)

            # Create regions and sites
            for region, sites in locations.items():
                region_params = dict(name=region, slug=self.slugify(region))
                region_info = self.__nb.dcim.regions.create(region_params)

                # Create sites
                for site in sites:
                    rrs_count = 0
                    device_pos = 0
                    site_params = dict(name=site, slug=self.slugify(site), region=region_info.id, status=STATUS_ACTIVE, tenant=tenants_info.id, tenant_group=tenant_groups_info.id)
                    site_info = self.__nb.dcim.sites.create(site_params)

                    # Create rack for each site
                    rrs_count = rrs_count + 1
                    rack_name = f'{region_info.slug}-{site_info.slug}-rack{rrs_count}'
                    rack_params = dict(name=rack_name, site=site_info.id, tenant=tenants_info.id, tenant_group=tenant_groups_info.id, status=STATUS_ACTIVE, u_height=RACK_HEIGHT)
                    rack_info = self.__nb.dcim.racks.create(rack_params)

                    # Create device (name, role, status, tenant, tenant_group, site, rack, manufacturer, device_type, platforms?)
                    # Create Cisco switch
                    device_pos = device_pos + 1
                    device_switch_name = f'{region_info.slug}-{site_info.slug}-rack{rrs_count}-csw{rrs_count}'
                    device_switch_params = dict(name=device_switch_name, 
                                                device_role=switch_device_role_info.id,
                                                status=STATUS_ACTIVE,
                                                tenant=tenants_info.id,
                                                tenant_group=tenant_groups_info.id,
                                                site=site_info.id, rack=rack_info.id,
                                                manufacturer=cisco_manufacturer_info.slug,
                                                device_type=device_type_cisco_switch_info.id,
                                                position=device_pos,
                                                face=RACK_POS)
                    device_switch_info = self.__nb.dcim.devices.create(device_switch_params)

                    # Create Cisco router
                    device_pos = device_pos + 1
                    device_router_name = f'{region_info.slug}-{site_info.slug}-rack{rrs_count}-cr{rrs_count}'
                    device_router_params = dict(name=device_router_name,
                                                device_role=router_device_role_info.id,
                                                status=STATUS_ACTIVE,
                                                tenant=tenants_info.id,
                                                tenant_group=tenant_groups_info.id,
                                                site=site_info.id, rack=rack_info.id,
                                                manufacturer=cisco_manufacturer_info.slug,
                                                device_type=device_type_cisco_router_info.id,
                                                position=device_pos,
                                                face=RACK_POS)

                    device_switch_info = self.__nb.dcim.devices.create(device_router_params)
        except pynetbox.RequestError as e:
            print(e.error)

            '''
            # Create rack for each sites->regions
            racks_count = 0
            regions_info = self.__nb.dcim.regions.all()
            for region_info in regions_info:

                # Get site name by region
                sites_name = self.__nb.dcim.sites.filter(region=region_info.slug)
                for site_name in sites_name:

                    # Get site id by site name
                    site_info = self.__nb.dcim.sites.get(name=site_name)

                    # Create rack for each site
                    racks_count = racks_count + 1
                    rack_name = f'{region_info.slug}-{site_info.slug}-rack{racks_count}'
                    rack_params = dict(name=rack_name, site=site_info.id, tenant=tenants_info.id, tenant_group=tenant_groups_info.id, status=STATUS_ACTIVE)
                    self.__nb.dcim.racks.create(rack_params)

            # Create rack for CH BE
            racks_count = 1
            ch_region_info = self.__nb.dcim.regions.get(slug=self.slugify("CH"))
            be_site_info = self.__nb.dcim.sites.get(slug=self.slugify("BE"))
            ch_ge_rack_name = f'{ch_region_info.slug}-{be_site_info.slug}-rack{racks_count}'
            ch_ge_rack_params = dict(name=ch_ge_rack_name, site=be_site_info.id, tenant=tenants_info.id, tenant_group=tenant_groups_info.id, status=STATUS_ACTIVE)
            self.__nb.dcim.racks.create(ch_ge_rack_params)


            # Create rack for US NY
            racks_count = racks_count + 1
            us_region_info = self.__nb.dcim.regions.get(slug=self.slugify("US"))
            ny_site_info = self.__nb.dcim.sites.get(slug=self.slugify("NY"))
            us_ny_rack_name = f'{us_region_info.slug}-{ny_site_info.slug}-rack{racks_count}'
            us_ny_rack_params = dict(name=us_ny_rack_name, site=ny_site_info.id, tenant=tenants_info.id, tenant_group=tenant_groups_info.id, status=STATUS_ACTIVE)
            self.__nb.dcim.racks.create(us_ny_rack_params)
            
            '''


    # Format slug from name
    def slugify(self, name):
        return re.sub(' +', ' ', name.lower()).replace(" ", "-")


if __name__ == "__main__":
    nb = Netbox()
    nb.create_network({"CH": ["GE", "BE"], "US": ["SF", "NY"]}, {"t": "Etienne", "tg": "Guignard"})
