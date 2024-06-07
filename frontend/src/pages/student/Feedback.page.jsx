import styles from './Feedback.page.module.scss';
import { Page } from '@shared/ui';
import { Button } from '@shared/ui';
import { StudentFeedback } from '@features/feedback';
export default function FeedbackPage() {
	return (
		<Page title="Обратная связь">
			<StudentFeedback />
			<Button className={styles.button} title="Выберите тренера" downArrow />
		</Page>
	);
}
