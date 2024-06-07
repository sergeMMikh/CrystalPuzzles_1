import { Page } from '@shared/ui';
import { Button } from '@shared/ui';
import styles from './Create.schedule.page.module.scss';
import CalendarTable from '@widgets/calendar.table';

export default function CreateShedulePage() {
	return (
		<Page title="Составить расписание тренеров">
			<CalendarTable />
			<div className={styles.buttons_container}>
				<Button title="Выберите тренера" downArrow />
				<Button title="Выберите площадку" downArrow />
				<Button title="Отправить расписание" />
			</div>
		</Page>
	);
}
