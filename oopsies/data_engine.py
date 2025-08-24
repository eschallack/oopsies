import datetime
from typing import Any
from faker import Faker
from faker.providers.date_time import Provider as DateTimeProvider
from faker.providers.misc import Provider as MiscProvider

class DataGenerators:
    def _generate_date(generator: DateTimeProvider, _: Any) -> datetime.date:
        return generator.date_time().date()
    def _generate_date_time(generator: DateTimeProvider, _: Any) -> datetime.date:
        return generator.date_time()
    def _generate_time(generator: DateTimeProvider, _: Any) -> datetime.time:
        return generator.date_time().time()
    def _generate_uuid(generator: MiscProvider, _: Any) -> bytes:
        return generator.uuid4()
    def _generate_null(generator: MiscProvider, _: Any) -> bytes:
        return None
