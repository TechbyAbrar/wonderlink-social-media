from django.core.management.base import BaseCommand
from locations.models import Country, Continent

class Command(BaseCommand):
    help = "Fill continent field for countries based on country_code"

    def handle(self, *args, **options):
        # Mapping of continent names to country codes
        continent_mapping = {
            "Asia": [
                "ae", "af", "am", "az", "bd", "bh", "bn", "bt", "cn", "ge", "hk", "id",
                "in", "iq", "ir", "il", "jo", "jp", "kg", "kh", "kp", "kr", "kw", "kz",
                "la", "lb", "lk", "mm", "mn", "my", "np", "om", "ph", "pk", "qa", "sa",
                "sg", "sy", "th", "tj", "tl", "tm", "tr", "tw", "uz", "vn", "ye", "cy"
            ],
            "Europe": [
                "ad", "al", "at", "ax", "ba", "be", "bg", "by", "ch", "cz", "de", "dk",
                "ee", "es", "fi", "fo", "fr", "gb", "gb-eng", "gb-nir", "gb-sct", "gb-wls",
                "gi", "gr", "hr", "hu", "ie", "im", "is", "it", "je", "li", "lt", "lu",
                "lv", "mc", "md", "me", "mk", "mt", "nl", "no", "pl", "pt", "ro", "rs",
                "ru", "se", "si", "sk", "sm", "ua", "va"
            ],
            "Africa": [
                "ao", "bf", "bi", "bj", "bw", "cd", "cf", "cg", "ci", "cm", "cv", "dj",
                "dz", "eg", "eh", "er", "et", "ga", "gh", "gm", "gn", "gq", "gw", "ke",
                "km", "lr", "ls", "ly", "ma", "mg", "ml", "mr", "mu", "mw", "mz", "na",
                "ne", "ng", "re", "rw", "sc", "sd", "sh", "sl", "sn", "so", "ss", "st",
                "sz", "td", "tg", "tn", "tz", "ug", "yt", "za", "zm", "zw"
            ],
            "North America": [
                "ag", "ai", "aw", "bb", "bl", "bm", "bq", "bs", "bz", "ca", "cr", "cu",
                "cw", "dm", "do", "gd", "gl", "gp", "gt", "hn", "ht", "jm", "kn", "ky",
                "lc", "mf", "mq", "ms", "mx", "ni", "pa", "pm", "pr", "sv", "sx", "tc",
                "tt", "us", "vc", "vg", "vi"
            ],
            "South America": [
                "ar", "bo", "br", "cl", "co", "ec", "gf", "gy", "pe", "py", "sr", "uy", "ve"
            ],
            "Australia (Oceania)": [
                "as", "au", "cc", "ck", "fj", "fm", "gu", "ki", "mh", "mp", "nc", "nf",
                "nr", "nu", "nz", "pg", "pw", "sb", "tk", "to", "tv", "vu", "wf", "ws"
            ],
            "Antarctica": [
                "aq", "hm", "tf"
            ]
        }

        for continent_name, country_codes in continent_mapping.items():
            # Create continent if it does not exist
            continent, created = Continent.objects.get_or_create(name=continent_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created continent: {continent_name}"))

            # Update countries
            updated_count = Country.objects.filter(country_code__in=country_codes).update(continent=continent)
            self.stdout.write(self.style.SUCCESS(
                f"{updated_count} countries updated to continent {continent_name}"
            ))

        self.stdout.write(self.style.SUCCESS("All countries have been successfully assigned to continents."))
