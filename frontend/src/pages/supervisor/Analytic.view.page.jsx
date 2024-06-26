import Page from '@shared/ui/page/Page';
import Button from '@shared/ui/button/Button';
import styles from './Analytics.view.page.module.scss';
import { Card, UserCard } from '@shared/card';
import { useState } from 'react';
import { CalendarButton } from '@features/calendar';

export default function AnalyticViewPage() {
	const [comment, setComment] = useState(false);

	return (
		<Page title="Аналитика">
			<UserCard img={''} name="Дмитриева Анастасия Алексеевна" showBtn>
				<ul className={styles.list}>
					<li>Часов обучения</li>
					<li>Количество учеников</li>
					<li>Сложность групп</li>
				</ul>
			</UserCard>

			<Card className={styles.comment} onClick={() => setComment(!comment)}>
				{comment ? <p>Комментарий</p> : <p>Комментарий тренера</p>}
			</Card>

			<div className={styles.buttons}>
				<CalendarButton />
				<Button title="Выгрузить" />
				<Button title="Открыть в Google doc" />
			</div>
		</Page>
	);
}
